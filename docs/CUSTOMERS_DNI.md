# Sistema de Clientes con DNI como Identificador Único

## 🎯 Estructura Final

```sql
CREATE TABLE customers (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    dni             TEXT UNIQUE NOT NULL,      -- ✅ Identificador único
    customer_number TEXT NOT NULL,             -- ⚠️ Puede tener duplicados
    phone           TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

## 🔑 Identificadores

| Campo | Tipo | Único | Propósito |
|---|---|---|---|
| `id` | SERIAL | ✅ | ID interno de BD |
| `dni` | TEXT | ✅ | **Identificador único del cliente** |
| `customer_number` | TEXT | ❌ | Número para factura (se reinicia al llegar al máx) |

## ⚙️ Comportamiento

### DNI (Identificador Principal)
- ✅ **UNIQUE** - Un DNI = Un cliente
- ✅ **REQUERIDO** - No se puede crear cliente sin DNI
- ✅ Se usa para **buscar** y **evitar duplicados**

### customer_number (Número de Factura)
- ❌ **NO UNIQUE** - Permite duplicados
- 🔄 Se **autogenera** siempre (900000XX)
- ⚠️ Se puede **reiniciar** al alcanzar el máximo
- 📄 Se usa solo para **mostrar en la factura**

## 💻 Uso en el Backend

### Crear/Buscar cliente (por DNI)
```python
# DNI es REQUERIDO
result = supabase_service.get_or_create_customer(
    name="Juan Pérez García",
    dni="12345678",          # ✅ REQUERIDO
    phone="+51 999 888 777"
)

# Si el DNI existe, retorna el cliente existente
# Si no existe, crea uno nuevo
```

### Buscar por DNI (recomendado)
```python
result = supabase_service.get_customer_by_dni("12345678")
if result['success']:
    customer = result['data']  # Retorna UN cliente (único)
```

### Buscar por customer_number (puede haber duplicados)
```python
result = supabase_service.get_customer_by_number("90000001")
if result['success']:
    customers = result['data']  # Retorna LISTA de clientes
```

## 🌐 Endpoints API

### GET `/api/invoice/customers/dni/{dni}` ⭐ Principal
Busca cliente por DNI (único)
```bash
curl http://localhost:8000/api/invoice/customers/dni/12345678
# Retorna: { "id": 1, "name": "Juan", "dni": "12345678", ... }
```

### GET `/api/invoice/customers/{customer_number}`
Busca por número de factura (puede haber múltiples)
```bash
curl http://localhost:8000/api/invoice/customers/90000001
# Retorna: { "count": 2, "customers": [...] }
```

### POST `/api/invoice/generate/pdf`
Genera factura (DNI requerido)
```typescript
fetch('/api/invoice/generate/pdf', {
  body: JSON.stringify({
    customer: {
      name: "Juan Pérez",
      dni: "12345678",     // ✅ REQUERIDO
      phone: "+51 999..."
    }
  })
});
```

## ✅ Validaciones

| Acción | DNI | customer_number |
|---|---|---|
| Crear cliente | ✅ Requerido | 🔄 Autogenerado |
| Buscar | ✅ Retorna 1 resultado | ⚠️ Puede retornar varios |
| Duplicados | ❌ No permite | ✅ Permite (se reinicia) |
| Identificación única | ✅ Sí | ❌ No |

## 🚀 Flujo Completo

1. **Frontend envía factura** con DNI del cliente
2. **Backend busca por DNI**:
   - Si existe → Reutiliza cliente (y su customer_number actual)
   - Si no existe → Crea nuevo cliente con nuevo customer_number
3. **BD genera customer_number** automáticamente (900000XX)
4. **PDF muestra customer_number** generado
5. Cuando customer_number llega a 99 → Se reinicia a 01
6. **No hay problema** porque DNI sigue siendo único

## 📝 Ejemplo Completo

```python
# Primera factura - DNI 12345678
result = supabase_service.get_or_create_customer(
    name="Juan Pérez", dni="12345678", phone="+51 999"
)
# Crea: { dni: "12345678", customer_number: "90000001" }

# Segunda factura - MISMO DNI 12345678
result = supabase_service.get_or_create_customer(
    name="Juan Pérez", dni="12345678", phone="+51 999"
)
# Encuentra cliente existente - customer_number sigue siendo "90000001"

# Tercera factura - DNI DIFERENTE 87654321
result = supabase_service.get_or_create_customer(
    name="María González", dni="87654321", phone="+51 988"
)
# Crea: { dni: "87654321", customer_number: "90000002" }

# ... muchas facturas después ...

# Factura #99 - DNI nuevo
result = supabase_service.get_or_create_customer(
    name="Cliente 99", dni="99999999", phone="+51 977"
)
# Crea: { dni: "99999999", customer_number: "90000099" }

# Factura #100 - DNI nuevo (customer_number se reinicia)
result = supabase_service.get_or_create_customer(
    name="Cliente 100", dni="11111111", phone="+51 966"
)
# Crea: { dni: "11111111", customer_number: "90000001" } ✅ Duplicado OK

# Ahora hay DOS clientes con customer_number "90000001":
# - DNI 12345678 (Juan Pérez)
# - DNI 11111111 (Cliente 100)

# Pero al buscar por DNI, cada uno es único:
get_customer_by_dni("12345678")  # → Juan Pérez
get_customer_by_dni("11111111")  # → Cliente 100
```

## 🎉 Ventajas de este Diseño

1. ✅ **DNI garantiza unicidad** de cada cliente
2. ✅ **customer_number puede reiniciarse** sin problemas
3. ✅ **No hay duplicados reales** (DNI los diferencia)
4. ✅ **Búsquedas confiables** por DNI
5. ✅ **Facturas muestran número corto** (90000XX)
