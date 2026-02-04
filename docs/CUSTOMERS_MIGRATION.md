# Migración: Tabla de Customers

## Descripción
Esta migración crea la tabla `customers` para almacenar información de clientes con número de cliente autoincremental.

## Características

### 1. Tabla `customers`
- **id**: ID autoincremental (PRIMARY KEY)
- **name**: Nombre completo del cliente (requerido)
- **customer_number**: Número único con formato `9000XX` (autogenerado)
- **email**: Email del cliente (opcional)
- **phone**: Teléfono del cliente (opcional)
- **address**: Dirección (opcional)
- **city**: Ciudad (opcional)
- **state**: Estado/Departamento (opcional)
- **zip_code**: Código postal (opcional)
- **country**: País (default: 'Peru')
- **created_at**: Fecha de creación
- **updated_at**: Fecha de última actualización

### 2. Función `generate_customer_number()`
Genera automáticamente el próximo número de cliente:
- Formato: `9000XX` donde XX se autoincrementa
- Ejemplos: `900001`, `900002`, `900003`, ..., `900099`, `9000100`

### 3. Triggers Automáticos
- **trigger_set_customer_number**: Genera `customer_number` automáticamente al insertar
- **trigger_update_customers_updated_at**: Actualiza `updated_at` automáticamente

### 4. Índices
- `idx_customers_customer_number`: Para búsquedas rápidas por número
- `idx_customers_name`: Para búsquedas por nombre

## Aplicar la Migración

### Opción 1: Supabase CLI (Recomendado)
```bash
cd /home/luis/Project/supabase
supabase db push
```

### Opción 2: Supabase Dashboard
1. Ve a tu proyecto en https://app.supabase.com
2. Navega a **SQL Editor**
3. Copia el contenido de `20260203000000_create_customers_table.sql`
4. Pega y ejecuta el script

### Opción 3: psql
```bash
psql -h <tu-host> -U postgres -d postgres -f supabase/migrations/20260203000000_create_customers_table.sql
```

## Uso en el Backend

### 1. Crear un nuevo cliente
```python
from app.services.supabase_service import supabase_service

# El customer_number se genera automáticamente
result = supabase_service.create_customer(
    name="Juan Pérez García",
    email="juan@example.com",
    phone="+51 999 888 777"
)

if result['success']:
    customer = result['data']
    print(f"Cliente creado: {customer['customer_number']}")
    # Output: Cliente creado: 900001
```

### 2. Obtener o crear cliente (evita duplicados)
```python
# Busca por nombre exacto, si no existe lo crea
result = supabase_service.get_or_create_customer(
    name="María González",
    email="maria@example.com"
)

if result['success']:
    customer = result['data']
    is_new = result['is_new']
    print(f"{'Nuevo' if is_new else 'Existente'}: {customer['customer_number']}")
```

### 3. Buscar cliente por número
```python
result = supabase_service.get_customer_by_number("900001")
if result['success']:
    customer = result['data']
    print(f"Cliente: {customer['name']}")
```

### 4. Buscar clientes por nombre
```python
result = supabase_service.get_customer_by_name("Juan")
if result['success']:
    for customer in result['data']:
        print(f"{customer['customer_number']}: {customer['name']}")
```

## Uso en las Facturas

### Antes (Frontend generaba número random)
```typescript
// ❌ Antiguo: número aleatorio sin persistencia
customer: {
  name: customerData?.full_name || "Cliente sin nombre",
  customer_number: `9000${Math.floor(Math.random() * 100).toString().padStart(2, '0')}`
}
```

### Ahora (Backend genera y persiste)
```typescript
// ✅ Nuevo: el backend gestiona todo automáticamente
const response = await fetch('/api/invoice/generate/pdf', {
  method: 'POST',
  body: JSON.stringify({
    customer: {
      name: customerData?.full_name || "Cliente sin nombre",
      email: customerData?.email,  // Opcional
      phone: customerData?.phone,  // Opcional
      // customer_number NO es necesario, se genera automáticamente
    },
    products: [...],
    invoice_info: {...}
  })
});

// El customer_number viene en el header de respuesta
const customerNumber = response.headers.get('X-Customer-Number');
console.log(`Cliente asignado: ${customerNumber}`);
```

## Endpoints Nuevos

### GET `/api/invoice/customers/{customer_number}`
Obtiene información de un cliente específico
```bash
curl http://localhost:8000/api/invoice/customers/900001
```

### GET `/api/invoice/customers/search/{name}`
Busca clientes por nombre
```bash
curl http://localhost:8000/api/invoice/customers/search/Juan
```

## Beneficios

1. ✅ **Persistencia**: Los números de cliente se guardan en la base de datos
2. ✅ **Autoincremento**: Cada nuevo cliente recibe un número único consecutivo
3. ✅ **Evita duplicados**: `get_or_create_customer` reutiliza clientes existentes
4. ✅ **Trazabilidad**: Puedes consultar historial de facturas por cliente
5. ✅ **Datos adicionales**: Almacena email, teléfono, dirección, etc.
6. ✅ **Header de respuesta**: El frontend recibe el `customer_number` generado

## Verificar que Funciona

Después de aplicar la migración:

```sql
-- Ver la tabla creada
SELECT * FROM customers;

-- Insertar un cliente de prueba (customer_number se genera automáticamente)
INSERT INTO customers (name, email, phone) 
VALUES ('Test Cliente', 'test@example.com', '+51 999 000 000');

-- Ver el customer_number generado
SELECT customer_number, name FROM customers;
-- Resultado: 900001 | Test Cliente

-- Insertar otro cliente
INSERT INTO customers (name) VALUES ('Otro Cliente');

-- Ver ambos
SELECT customer_number, name FROM customers ORDER BY id;
-- Resultado: 
-- 900001 | Test Cliente
-- 900002 | Otro Cliente
```

## Notas Importantes

- El `customer_number` comienza en `900001` y se incrementa automáticamente
- Si insertas manualmente un `customer_number`, debe seguir el formato `9000XX`
- La función `get_or_create_customer` evita duplicados buscando por nombre exacto
- El campo `name` es el único requerido, los demás son opcionales
- Los timestamps `created_at` y `updated_at` se gestionan automáticamente
