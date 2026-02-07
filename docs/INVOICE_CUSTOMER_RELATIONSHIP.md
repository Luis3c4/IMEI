# Invoice-Customer Relationship

## 📋 Overview

Este documento describe la implementación de la relación entre las tablas `invoices` y `customers` mediante una foreign key.

**Fecha de implementación:** 7 de febrero, 2026  
**Migración:** `20260207000000_add_customer_id_to_invoices.sql`

---

## 🎯 Objetivo

Relacionar cada factura (`invoice`) con el cliente (`customer`) que la generó, utilizando el DNI único del cliente como identificador confiable.

### Beneficios:
- ✅ **Historial de compras:** Consultar todas las facturas de un cliente específico
- ✅ **Integridad referencial:** Evitar eliminación de clientes con historial de compras
- ✅ **Datos consistentes:** Vinculación automática usando DNI único
- ✅ **Reutilización de clientes:** Mismo cliente para múltiples compras, sin duplicación

---

## 🔧 Cambios Implementados

### 1. **Base de Datos** ([20260207000000_add_customer_id_to_invoices.sql](supabase/migrations/20260207000000_add_customer_id_to_invoices.sql))

```sql
-- Nueva columna (nullable para compatibilidad con facturas históricas)
ALTER TABLE invoices 
ADD COLUMN customer_id INTEGER NULL;

-- Foreign key con protección
ALTER TABLE invoices
ADD CONSTRAINT fk_invoices_customer_id 
FOREIGN KEY (customer_id) 
REFERENCES customers(id) 
ON DELETE RESTRICT;

-- Índice para queries eficientes
CREATE INDEX idx_invoices_customer_id ON invoices(customer_id);
```

**Decisiones de diseño:**
- `customer_id` es **NULLABLE**: Facturas antiguas (creadas antes de la migración) no tienen relación
- `ON DELETE RESTRICT`: No se puede eliminar un customer si tiene facturas asociadas
- Índice: Optimiza queries como "dame todas las facturas del cliente X"

---

### 2. **Backend: InvoiceRepository** ([invoice_repository.py](IMEI/app/services/supabase/invoice_repository.py))

#### Método actualizado: `create_invoice()`

```python
def create_invoice(
    self, 
    invoice_number: str, 
    invoice_date: str, 
    customer_id: int = None  # ← NUEVO parámetro
) -> Dict[str, Any]:
```

- Ahora acepta `customer_id` opcional
- Si se proporciona, se incluye en el INSERT
- El trigger de `customer_number` sigue funcionando independientemente

#### Nuevo método: `get_invoices_by_customer_id()`

```python
def get_invoices_by_customer_id(self, customer_id: int) -> Dict[str, Any]:
    """
    Obtiene todas las facturas de un cliente por su ID.
    Útil para: historial de compras, reportes, análisis.
    """
```

---

### 3. **Backend: Flujo de Creación** ([invoice_routes.py](IMEI/app/routes/invoice_routes.py))

#### **ANTES** (orden incorrecto):
```python
1. Crear invoice → obtener customer_number
2. Crear/buscar customer por DNI
3. Generar PDF
```

#### **DESPUÉS** (orden correcto con FK):
```python
1. Crear/buscar customer por DNI → obtener customer.id
2. Crear invoice con customer_id (FK apunta a customer)
3. Generar PDF con customer_number auto-generado
```

**Código actualizado:**
```python
# Paso 1: Obtener o crear cliente PRIMERO (usando DNI único)
customer_result = supabase_service.customers.get_or_create_customer(
    name=request.customer.name,
    dni=request.customer.dni,
    phone=request.customer.phone
)
customer_id = customer_result['data']['id']

# Paso 2: Crear factura con relación al customer
invoice_result = supabase_service.invoices.create_invoice(
    invoice_number=request.invoice_info.invoice_number,
    invoice_date=request.invoice_info.invoice_date,
    customer_id=customer_id  # ← FK a customers.id
)
```

---

## 📊 Estructura de Datos

### Tabla `invoices` (actualizada)

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | ID único de factura |
| `customer_number` | TEXT | NOT NULL | Auto-generado (900000XX) para display en PDF |
| `invoice_number` | TEXT | NOT NULL, UNIQUE | Número de factura (frontend) |
| `invoice_date` | TEXT | NOT NULL | Fecha de factura |
| `customer_id` | **INTEGER** | **NULL, FK → customers.id** | **Relación con customer** |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha de creación |

### Tabla `customers` (sin cambios)

| Columna | Tipo | Constraints | Descripción |
|---------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY | ID único de cliente |
| `dni` | TEXT | NOT NULL, UNIQUE | DNI (identificador único real) |
| `name` | TEXT | NOT NULL | Nombre completo |
| `phone` | TEXT | NULL | Teléfono |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Fecha de creación |

---

## 🔄 Flujo Completo

### Caso: Cliente nuevo hace su primera compra

```
Frontend → Backend API
  │
  ├─► Request: { customer: { name, dni, phone }, products: [...] }
  │
  └─► Backend:
       │
       ├─► 1. get_or_create_customer(dni="12345678")
       │    └─► Busca por DNI → No existe → Crea nuevo
       │        ✅ customers: { id: 1, dni: "12345678", name: "Juan", ... }
       │
       ├─► 2. create_invoice(customer_id=1)
       │    └─► Inserta con FK → Trigger genera customer_number
       │        ✅ invoices: { id: 1, customer_id: 1, customer_number: "90000001", ... }
       │
       └─► 3. Generar PDF con customer_number "90000001"
            └─► Response: PDF + Headers (X-Customer-Number, X-Invoice-Id)
```

### Caso: Cliente existente hace segunda compra

```
Frontend → Backend API
  │
  ├─► Request: { customer: { name, dni, phone }, products: [...] }
  │
  └─► Backend:
       │
       ├─► 1. get_or_create_customer(dni="12345678")
       │    └─► Busca por DNI → SÍ existe → Retorna existente
       │        ✅ customers: { id: 1, dni: "12345678", ... } (sin duplicar)
       │
       ├─► 2. create_invoice(customer_id=1)
       │    └─► Inserta con FK → Trigger genera NUEVO customer_number
       │        ✅ invoices: { id: 15, customer_id: 1, customer_number: "90000015", ... }
       │
       └─► 3. Generar PDF con customer_number "90000015"
```

**Resultado:**
- `customers` table: 1 registro (dni único)
- `invoices` table: 2 registros (ambos con `customer_id = 1`)

---

## 🔍 Queries Útiles

### Obtener todas las facturas de un cliente (por DNI)
```python
# 1. Buscar customer por DNI
customer = supabase_service.customers.get_by_dni("12345678")
customer_id = customer['data']['id']

# 2. Obtener todas sus facturas
invoices = supabase_service.invoices.get_invoices_by_customer_id(customer_id)
```

### SQL directo (Supabase Dashboard)
```sql
-- Todas las facturas con datos del cliente
SELECT 
    i.invoice_number,
    i.customer_number,
    i.invoice_date,
    c.name AS customer_name,
    c.dni,
    c.phone
FROM invoices i
LEFT JOIN customers c ON i.customer_id = c.id
ORDER BY i.created_at DESC;

-- Facturas de un cliente específico por DNI
SELECT i.*
FROM invoices i
INNER JOIN customers c ON i.customer_id = c.id
WHERE c.dni = '12345678'
ORDER BY i.created_at DESC;

-- Clientes con cantidad de facturas
SELECT 
    c.id,
    c.name,
    c.dni,
    COUNT(i.id) AS total_invoices
FROM customers c
LEFT JOIN invoices i ON c.id = i.customer_id
GROUP BY c.id, c.name, c.dni
ORDER BY total_invoices DESC;
```

---

## ⚠️ Consideraciones Importantes

### 1. **Facturas históricas**
- Facturas creadas ANTES de esta migración tienen `customer_id = NULL`
- No hay forma automática de relacionarlas (no se guardaba DNI en invoices)
- El sistema sigue funcionando normalmente, el `customer_id` es opcional

### 2. **customer_number vs customer_id**
- **`customer_number`**: Campo de display (900000XX), se reinicia después del 99, solo para PDFs
- **`customer_id`**: FK real, nunca cambia, identifica al cliente de forma única
- **NO reemplazar customer_number con customer_id en PDFs** (mantener diseño actual)

### 3. **Protección de datos**
```python
# ❌ NO se puede eliminar un customer con facturas
DELETE FROM customers WHERE id = 1;
# → ERROR: violates foreign key constraint "fk_invoices_customer_id"

# ✅ Para eliminar un customer, primero hay que:
# 1. Eliminar todas sus facturas, O
# 2. Cambiar la constraint a ON DELETE SET NULL (no recomendado)
```

### 4. **DNI como identificador único**
- El DNI es el verdadero identificador único del cliente
- `customer_id` es solo para la FK en base de datos
- Siempre buscar/crear customers por DNI, no por customer_number

---

## 🚀 Próximos Pasos (Opcional)

### Features futuras habilitadas:
1. **Historial de compras del cliente**
   - Endpoint: `GET /api/customers/{dni}/invoices`
   - Mostrar todas las facturas de un cliente en el frontend

2. **Estadísticas por cliente**
   - Total gastado, productos más comprados, frecuencia de compra

3. **Búsqueda mejorada**
   - Buscar facturas por nombre del cliente (JOIN con customers)

4. **Reportes**
   - Clientes más frecuentes, tickets promedio, etc.

---

## 📝 Testing

### Test 1: Crear factura con cliente nuevo
```bash
POST /api/invoice/generate/pdf
{
  "customer": {
    "name": "Test User",
    "dni": "99999999",
    "phone": "999888777"
  },
  "products": [...],
  "invoice_info": {...}
}

# Verificar:
# 1. customers table tiene 1 registro con dni="99999999"
# 2. invoices table tiene 1 registro con customer_id apuntando al customer
# 3. customer_number se generó correctamente (900000XX)
# 4. PDF muestra customer_number, no customer_id
```

### Test 2: Crear segunda factura para mismo cliente
```bash
POST /api/invoice/generate/pdf
{
  "customer": {
    "name": "Test User",
    "dni": "99999999",  # ← Mismo DNI
    "phone": "999888777"
  },
  "products": [...],
  "invoice_info": {...}
}

# Verificar:
# 1. customers table SIGUE teniendo 1 solo registro (no duplicado)
# 2. invoices table tiene 2 registros, ambos con el mismo customer_id
# 3. Cada factura tiene diferente customer_number (90000001, 90000002)
```

### Test 3: Intentar eliminar customer con facturas
```sql
-- En Supabase Dashboard
DELETE FROM customers WHERE dni = '99999999';

-- Debe fallar con error:
-- ERROR: update or delete on table "customers" violates foreign key constraint
```

### Test 4: Consultar facturas por customer_id
```python
# Obtener customer_id del DNI
customer = supabase_service.customers.get_by_dni("99999999")
customer_id = customer['data']['id']

# Obtener todas sus facturas
invoices = supabase_service.invoices.get_invoices_by_customer_id(customer_id)

# Verificar que retorna las 2 facturas creadas en Test 1 y 2
```

---

## 📚 Referencias

- [Archivo de migración](supabase/migrations/20260207000000_add_customer_id_to_invoices.sql)
- [InvoiceRepository](IMEI/app/services/supabase/invoice_repository.py)
- [invoice_routes.py](IMEI/app/routes/invoice_routes.py)
- [CUSTOMERS_DNI.md](CUSTOMERS_DNI.md) - Diseño original del sistema de customers
- [SUPABASE_ARCHITECTURE.md](SUPABASE_ARCHITECTURE.md) - Arquitectura general

---

**Autor:** Sistema automatizado  
**Última actualización:** 7 de febrero, 2026
