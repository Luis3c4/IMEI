# Arquitectura Modular de Supabase

## 📋 Resumen

El servicio de Supabase ha sido refactorizado de un servicio monolítico (638 líneas) a una arquitectura modular basada en **Repository Pattern** con **Facade Híbrido**. Esta nueva estructura mejora la mantenibilidad, testabilidad y escalabilidad del código.

---

## 🏗️ Estructura de Archivos

```
app/services/
├── supabase/                          # Módulo de repositorios
│   ├── __init__.py                    # Exports públicos
│   ├── base.py                        # BaseSupabaseRepository (Singleton)
│   ├── device_repository.py          # Gestión de devices + consulta_history
│   ├── product_repository.py         # Gestión de products + variants + items
│   └── customer_repository.py        # Gestión de customers
└── supabase_service.py                # Facade híbrido (retrocompatibilidad)
```

---

## 🔑 Conceptos Clave

### 1. **Cliente Singleton Compartido**

Todos los repositorios comparten una **única instancia del cliente Supabase** para eficiencia:

```python
# app/services/supabase/base.py
_supabase_client: Optional[Client] = None  # Variable global compartida

class BaseSupabaseRepository:
    def __init__(self):
        self.client = self._get_client()  # Reutiliza cliente existente
```

**Ventajas:**
- ✅ Una sola conexión a Supabase
- ✅ Menor uso de memoria
- ✅ Inicialización más rápida

---

### 2. **Repositorios por Dominio**

Cada repositorio gestiona una entidad del dominio:

| Repositorio | Responsabilidad | Tablas |
|------------|-----------------|--------|
| **DeviceRepository** | Dispositivos e historial | `devices`, `consulta_history` |
| **ProductRepository** | Productos, variantes e inventario | `products`, `product_variants`, `product_items` |
| **CustomerRepository** | Clientes | `customers` |

---

### 3. **Facade Híbrido**

El `SupabaseService` actúa como **puente** entre el código legacy y la nueva arquitectura:

```python
class SupabaseService:
    def __init__(self):
        # Repositorios públicos (uso moderno)
        self.devices = DeviceRepository()
        self.products = ProductRepository()
        self.customers = CustomerRepository()
    
    # Métodos legacy para retrocompatibilidad
    def save_device_query(self, ...):
        return self.products.save_device_query(...)  # Delega
```

---

## 📖 Guía de Uso

### Opción 1: **Uso Moderno** (Recomendado)

Acceso directo a través de los repositorios del facade:

```python
from app.services.supabase_service import supabase_service

# Productos
result = supabase_service.products.save_device_query(
    device_info=device_data,
    metadata=metadata,
    parsed_model=parsed_model
)

products = supabase_service.products.get_products_with_variants()

# Clientes
customer = supabase_service.customers.get_or_create_customer(
    name="Juan Pérez",
    dni="12345678",
    phone="+51999888777"
)

# Dispositivos
device = supabase_service.devices.get_device(imei="123456789012345")
```

**Ventajas:**
- ✅ Código más explícito y semántico
- ✅ Fácil de testear (mockear solo `products` o `customers`)
- ✅ Preparado para futuras refactorizaciones

---

### Opción 2: **Uso Legacy** (Retrocompatibilidad)

Métodos directos del facade (deprecados con warnings):

```python
from app.services.supabase_service import supabase_service

# Funciona, pero genera DeprecationWarning
result = supabase_service.save_device_query(...)
customer = supabase_service.get_or_create_customer(...)
```

**⚠️  Warnings emitidos:**
```
DeprecationWarning: save_device_query() está deprecado. 
Usa supabase_service.products.save_device_query()
```

---

### Opción 3: **Uso Directo de Repositorios** (Avanzado)

Instanciar repositorios independientemente:

```python
from app.services.supabase import ProductRepository, CustomerRepository

product_repo = ProductRepository()
customer_repo = CustomerRepository()

result = product_repo.save_device_query(...)
customer = customer_repo.create_customer(...)
```

**Ventajas:**
- ✅ Máxima flexibilidad
- ✅ Ideal para testing unitario
- ✅ Sin dependencia del facade

---

## 🚀 Migración Gradual

### Plan de Migración Recomendado

#### **Fase 1: Sin Cambios (Actual)**
- ✅ Código legacy funciona sin modificaciones
- ✅ Warnings visibles en desarrollo para identificar uso deprecado

#### **Fase 2: Migración Progresiva** (Opcional)
Actualizar rutas a uso moderno:

```python
# ANTES (devices.py)
supabase_result = supabase_service.save_device_query(...)

# DESPUÉS
supabase_result = supabase_service.products.save_device_query(...)
```

#### **Fase 3: Eliminación de Legacy** (Futuro)
Cuando todo el código use la nueva sintaxis, eliminar métodos legacy.

---

## 🔍 Casos de Uso Principales

### 1. **Consulta de Dispositivo (Flujo Completo)**

```python
# app/routes/devices.py (línea 147)
from app.services.supabase_service import supabase_service

supabase_result = supabase_service.products.save_device_query(
    device_info=result['data'],
    metadata={
        'service_id': '219',
        'price': 1.0,
        'product_price': 499.0,
        'product_number': 'MLXX2LL/A'
    },
    parsed_model={
        'full_model': 'IPHONE 17 PRO MAX',
        'brand': 'IPHONE',
        'color': 'SILVER',
        'capacity': '512GB',
        'ram': None
    }
)

if supabase_result['success']:
    product_id = supabase_result['product_id']
    variant_id = supabase_result['variant_id']
    item_id = supabase_result['item_id']
```

**Qué hace internamente:**
1. Busca/crea el **Product** (`IPHONE 17 PRO MAX`)
2. Busca/crea la **Variant** (`SILVER`, `512GB`)
3. Crea el **Product Item** (serial único) con status `available`
4. Asigna el **Product Number** (desde metadata o estático)

---

### 2. **Gestión de Inventario**

```python
# app/routes/products.py (línea 66)
from app.services.supabase_service import supabase_service

# Obtener productos con stock
result = supabase_service.products.get_products_with_variants()

for product in result['data']:
    print(f"Producto: {product['name']}")
    for variant in product['product_variants']:
        print(f"  - {variant['color']} {variant['capacity']}: {variant['quantity']} disponibles")

# Actualizar status de item (venta)
update_result = supabase_service.products.update_product_item_status(
    item_id=123,
    new_status='sold'
)
```

---

### 3. **Gestión de Clientes**

```python
# app/routes/invoice_routes.py (línea 129)
from app.services.supabase_service import supabase_service

customer_result = supabase_service.customers.get_or_create_customer(
    name="Geraldine Eva Flores Flores",
    dni="12345678",
    phone="+51999888777"
)

if customer_result['success']:
    customer = customer_result['data']
    is_new = customer_result['is_new']
    print(f"Cliente: {customer['customer_number']} ({'nuevo' if is_new else 'existente'})")
```

---

## 🧪 Testing

### Mockear Repositorio Específico

```python
from unittest.mock import Mock

# Mock solo del repositorio de productos
supabase_service.products = Mock()
supabase_service.products.save_device_query.return_value = {
    'success': True,
    'product_id': 1,
    'variant_id': 2,
    'item_id': 3
}

# El resto de repositorios siguen funcionando normalmente
customer = supabase_service.customers.get_customer_by_dni("12345678")
```

---

## ⚙️ Detalles Técnicos

### Helper Movido a Parsers

La función `_clean_apple_watch_model` fue movida a `app/utils/parsers.py`:

```python
from app.utils.parsers import clean_apple_watch_model

model = clean_apple_watch_model("APPLE WATCH SERIES 11 49MM GPS")
# Resultado: "APPLE WATCH SERIES 11 GPS"
```

**Razón:** Es una función de parsing, no de persistencia.

---

### Imports Optimizados

Los imports de configuración ahora están al inicio de los archivos:

```python
# app/services/supabase/product_repository.py
from app.config.pricing_pnumbers import get_static_product_number  # Top-level
from app.utils.parsers import clean_apple_watch_model

# No hay imports circulares
```

---

### Eliminación de `raw_query()`

El método `raw_query()` fue **eliminado** porque:
- ❌ Nunca se usó en el proyecto
- ❌ Va contra el principio de repositorios específicos
- ❌ Genera código poco mantenible

Si en el futuro se necesita, agregar métodos específicos en cada repositorio.

---

## 📊 Comparación de Líneas de Código

| Archivo | Antes | Después | Cambio |
|---------|-------|---------|--------|
| `supabase_service.py` | 638 | 220 | -65% |
| `base.py` | - | 90 | +90 |
| `device_repository.py` | - | 180 | +180 |
| `product_repository.py` | - | 310 | +310 |
| `customer_repository.py` | - | 190 | +190 |
| **TOTAL** | **638** | **990** | +55% |

**Nota:** Aunque el total de líneas aumentó, cada archivo es más:
- ✅ Pequeño y enfocado (180-310 líneas vs 638)
- ✅ Fácil de entender y navegar
- ✅ Testeable de forma independiente

---

## 🔐 Consideraciones de Seguridad

### Validación en Repositorios

Los repositorios mantienen validaciones críticas:

```python
# ProductRepository.update_product_item_status()
valid_statuses = ['available', 'sold', 'reserved']
if new_status not in valid_statuses:
    return {'success': False, 'error': 'Status inválido'}
```

### Manejo de Conexiones

El cliente Singleton maneja automáticamente:
- ⚠️  Credenciales faltantes (retorna `None` sin crashear)
- 🔄 Reintentos de conexión via `is_connected()`
- 📝 Logging de errores de conexión

---

## 🐛 Troubleshooting

### Problema: "Module supabase has no attribute 'DeviceRepository'"

**Causa:** Import incorrecto  
**Solución:**
```python
# ❌ MAL
from app.services import supabase
repo = supabase.DeviceRepository()

# ✅ BIEN
from app.services.supabase import DeviceRepository
repo = DeviceRepository()

# ✅ O BIEN
from app.services.supabase_service import supabase_service
result = supabase_service.devices.get_device(imei)
```

---

### Problema: DeprecationWarning en logs

**Causa:** Uso de métodos legacy  
**Solución:** Migrar a uso moderno:
```python
# ❌ Legacy (genera warning)
result = supabase_service.save_device_query(...)

# ✅ Moderno
result = supabase_service.products.save_device_query(...)
```

---

### Problema: "Cliente de Supabase no inicializado"

**Causa:** Credenciales `SUPABASE_URL` o `SUPABASE_KEY` no configuradas  
**Solución:** Verificar `.env`:
```bash
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-anon-key
```

---

## 📚 Referencias

- **Código Legacy:** [supabase_service.py (commit anterior)](git show HEAD~1:app/services/supabase_service.py)
- **Repositorios:** [app/services/supabase/](app/services/supabase/)
- **Facade:** [supabase_service.py](app/services/supabase_service.py)
- **Parsers:** [app/utils/parsers.py](app/utils/parsers.py)

---

## ✅ Checklist de Migración

Cuando migres código a la nueva arquitectura:

- [ ] Cambiar `supabase_service.save_device_query()` → `supabase_service.products.save_device_query()`
- [ ] Cambiar `supabase_service.get_or_create_customer()` → `supabase_service.customers.get_or_create_customer()`
- [ ] Cambiar `supabase_service.get_products_with_variants()` → `supabase_service.products.get_products_with_variants()`
- [ ] Cambiar `supabase_service.update_product_item_status()` → `supabase_service.products.update_product_item_status()`
- [ ] Cambiar `supabase_service.insert_device()` → `supabase_service.devices.insert_device()`
- [ ] Verificar que no hay DeprecationWarnings en logs
- [ ] Probar endpoints en Bruno/Postman
- [ ] Actualizar documentación de API si es necesario

---

**Última actualización:** Febrero 4, 2026  
**Versión:** 1.0.0
