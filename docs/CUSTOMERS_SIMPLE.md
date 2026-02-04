# Tabla Customers - Documentación Simplificada

## 📋 Estructura de la Tabla

```sql
CREATE TABLE customers (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    dni             TEXT,
    customer_number TEXT UNIQUE NOT NULL,  -- Autogenerado: 900001, 900002, ...
    phone           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

## 🚀 Aplicar Migración

```bash
# Opción 1: Supabase CLI
cd /home/luis/Project/supabase
supabase db push

# Opción 2: Dashboard de Supabase
# Copia y ejecuta el contenido de 20260203000000_create_customers_table.sql
```

## ✨ Cómo Funciona

El `customer_number` se genera **automáticamente** con formato `9000XX`:
- Primer cliente: `900001`
- Segundo cliente: `900002`
- Tercer cliente: `900003`
- ...y así sucesivamente

## 💻 Uso en el Backend

### Crear cliente (automático al generar factura)
```python
from app.services.supabase_service import supabase_service

# El customer_number se genera automáticamente
result = supabase_service.create_customer(
    name="Juan Pérez García",
    dni="12345678",
    phone="+51 999 888 777"
)

if result['success']:
    print(f"Cliente: {result['data']['customer_number']}")
    # Output: Cliente: 900001
```

### Obtener o crear (evita duplicados)
```python
# Busca por nombre, si no existe lo crea
result = supabase_service.get_or_create_customer(
    name="María González",
    dni="87654321",
    phone="+51 988 777 666"
)

if result['success']:
    is_new = result['is_new']
    customer = result['data']
    print(f"{'Nuevo' if is_new else 'Existente'}: {customer['customer_number']}")
```

### Buscar por número
```python
result = supabase_service.get_customer_by_number("900001")
if result['success']:
    print(result['data']['name'])
```

### Buscar por nombre
```python
result = supabase_service.get_customer_by_name("Juan")
if result['success']:
    for customer in result['data']:
        print(f"{customer['customer_number']}: {customer['name']}")
```

## 🌐 Uso en el Frontend

### Generar Factura (TypeScript/React)
```typescript
const generateInvoice = async () => {
  const response = await fetch('/api/invoice/generate/pdf', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      order_date: "February 03, 2026",
      order_number: "W1234567890",
      customer: {
        name: "Juan Pérez García",  // ✅ Requerido
        dni: "12345678",            // ⚪ Opcional
        phone: "+51 999 888 777",   // ⚪ Opcional
        // customer_number NO es necesario - se genera automáticamente
      },
      products: [...],
      invoice_info: {...}
    })
  });

  // El customer_number generado viene en el header
  const customerNumber = response.headers.get('X-Customer-Number');
  console.log(`Cliente asignado: ${customerNumber}`);
  // Output: Cliente asignado: 900001
};
```

## 📡 Endpoints API

### POST `/api/invoice/generate/pdf`
Genera factura y crea/obtiene cliente automáticamente
- Retorna PDF descargable
- Header `X-Customer-Number` con el número generado

### POST `/api/invoice/preview`
Preview de factura (sin descargar)
- Retorna PDF inline
- También gestiona el cliente en BD

### GET `/api/invoice/customers/{customer_number}`
Obtiene información de un cliente
```bash
curl http://localhost:8000/api/invoice/customers/900001
```

### GET `/api/invoice/customers/search/{name}`
Busca clientes por nombre
```bash
curl http://localhost:8000/api/invoice/customers/search/Juan
```

## ✅ Verificación

Después de aplicar la migración:

```sql
-- Insertar cliente de prueba
INSERT INTO customers (name, dni, phone) 
VALUES ('Test Cliente', '11111111', '+51 999 000 000');

-- Ver el customer_number generado
SELECT * FROM customers;
-- Resultado:
-- id | name         | dni      | customer_number | phone          | created_at
-- 1  | Test Cliente | 11111111 | 900001          | +51 999 000 000| 2026-02-03...

-- Insertar otro cliente
INSERT INTO customers (name) VALUES ('Otro Cliente');

-- Ver ambos
SELECT customer_number, name FROM customers ORDER BY id;
-- Resultado:
-- 900001 | Test Cliente
-- 900002 | Otro Cliente
```

## 🎯 Resumen

| Característica | Estado |
|---|---|
| Tabla simplificada | ✅ Solo 6 campos |
| Autoincremento | ✅ customer_number automático |
| DNI | ✅ Campo opcional |
| Persistencia | ✅ Se guarda en PostgreSQL |
| API REST | ✅ 4 endpoints disponibles |
| Header respuesta | ✅ `X-Customer-Number` en PDF |
| Evita duplicados | ✅ `get_or_create_customer()` |

## 📝 Campos de la Tabla

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `id` | SERIAL | Auto | ID único autoincremental |
| `name` | TEXT | ✅ Sí | Nombre completo del cliente |
| `dni` | TEXT | ⚪ No | DNI del cliente |
| `customer_number` | TEXT | Auto | Número único (900001, 900002, ...) |
| `phone` | TEXT | ⚪ No | Teléfono del cliente |
| `created_at` | TIMESTAMP | Auto | Fecha de creación |
