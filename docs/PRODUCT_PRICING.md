# Product Pricing Service

Servicio para determinar precios de productos Apple basándose en el modelo y capacidad del dispositivo.

## 📁 Estructura

```
app/
├── config/
│   ├── __init__.py          # Exports de configuración
│   └── pricing.py           # Tabla de precios de productos (DATA)
└── services/
    └── product_pricing_service.py  # Lógica de búsqueda de precios (LOGIC)
```

## 🎯 Separación de Responsabilidades

### `app/config/pricing.py` - Configuración de Datos
- **Responsabilidad**: Almacenar la tabla de precios de productos
- **Contenido**: Diccionario `APPLE_PRICING_USD` con precios en USD
- **Actualización**: Fácil de mantener, solo actualizar valores
- **Funciones helper**: `get_all_models()`, `get_model_capacities()`, `get_price_range()`

### `app/services/product_pricing_service.py` - Lógica de Negocio
- **Responsabilidad**: Lógica para buscar y determinar precios
- **Funciones principales**:
  - `get_product_price()`: Busca el precio de un producto
  - `get_price_info()`: Retorna información completa del precio
  - `get_available_models()`: Lista todos los modelos disponibles
  - `get_model_variants()`: Obtiene variantes de un modelo

## 📝 Uso

```python
from app.services.product_pricing_service import product_pricing_service
from app.utils.parsers import parse_model_description

# Parsear modelo
parsed_model = parse_model_description('IPHONE 17 PRO MAX 512GB-USA')

# Obtener precio
price = product_pricing_service.get_product_price(parsed_model)
# Output: 1399.0

# Obtener información completa
info = product_pricing_service.get_price_info(parsed_model)
# Output: {
#     'product_price': 1399.0,
#     'currency': 'USD',
#     'price_found': True,
#     'message': 'Precio encontrado'
# }
```

## 🔍 Estrategia de Búsqueda

El servicio utiliza una estrategia de búsqueda en cascada:

1. **Coincidencia exacta con capacidad**
   - Busca el modelo exacto + capacidad específica
   - Ej: `IPHONE 17 PRO` + `512GB` → `$1399`

2. **Precio DEFAULT**
   - Para productos sin variantes de capacidad
   - Ej: `APPLE TV 4K` (sin capacidad) → `$129` (DEFAULT)

3. **Precio único**
   - Si solo hay una opción de precio, la retorna
   - Ej: `AIRPODS PRO` → `$249`

4. **Coincidencia parcial**
   - Busca modelos que empiecen con la clave
   - Útil para modelos con sufijos adicionales

## 🛠️ Manejo Especial

### Apple Watch
Para Apple Watch, el tamaño (41MM, 45MM) se extrae del nombre del modelo:
```python
# Input: 'APPLE WATCH SERIES 11 GPS 45MM'
# Extracción: capacity = '45MM'
# Búsqueda: APPLE_PRICING_USD['APPLE WATCH SERIES 11']['45MM']
```

## 📊 Actualización de Precios

Para actualizar precios, edita `app/config/pricing.py`:

```python
APPLE_PRICING_USD = {
    'IPHONE 18 PRO': {  # Nuevo modelo
        '128GB': 1199.0,
        '256GB': 1299.0,
        '512GB': 1499.0,
        '1TB': 1799.0,
    },
}
```

## ✅ Ventajas de esta Arquitectura

1. **Separación clara**: Datos (config) vs Lógica (service)
2. **Fácil mantenimiento**: Actualizar precios sin tocar lógica
3. **Testeable**: Lógica separada de datos facilita tests
4. **Escalable**: Fácil agregar nuevos modelos o monedas
5. **Documentado**: Estructura clara y bien comentada
6. **Type hints**: Código con tipos para mejor IDE support

## 🧪 Testing

```bash
# Test rápido
python3 -c "
from app.services.product_pricing_service import product_pricing_service
print(f'Modelos disponibles: {len(product_pricing_service.get_available_models())}')
"
```

## 📚 Recursos

- Precios oficiales: https://www.apple.com/shop
- Documentación API: Ver `/docs` endpoint de FastAPI
