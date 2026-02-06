# Mejoras RENIEC - Cache Local de Consultas

## Resumen de Cambios

Se implementó un sistema de cache local para las consultas de RENIEC que reduce significativamente el número de llamadas a la API externa, mejorando el rendimiento y reduciendo costos.

## Funcionalidad

### Antes
- Cada consulta de DNI hacía una llamada directa a la API externa de RENIEC
- No se guardaba información histórica de las consultas
- Mayor latencia y costo por consulta

### Ahora
1. **Verificación en BD primero**: Cuando se consulta un DNI, el sistema primero verifica si existe en la base de datos local
2. **Cache permanente**: Los datos de RENIEC son estáticos (nombres y apellidos no cambian), por lo que no requieren validación de vigencia
3. **Fallback automático**: Si no hay datos locales, se consulta la API externa
4. **Actualización automática**: Los nuevos datos de RENIEC se guardan automáticamente en la BD

## Cambios en Base de Datos

### Nueva Migración
**Archivo**: `20260206200000_add_reniec_fields_to_customers.sql`

Agrega a la tabla `customers`:
- `first_name` (TEXT): Nombres de la persona
- `first_last_name` (TEXT): Apellido paterno
- `second_last_name` (TEXT): Apellido materno

**Índices**:
- `idx_customers_dni`: Índice en columna DNI para búsquedas rápidas

## Cambios en el Código

### 1. CustomerRepository (`customer_repository.py`)
Nuevos métodos:
```python
# Obtiene datos de RENIEC de la BD si existen
get_customer_reniec_data(dni: str)

# Actualiza o crea un cliente con datos de RENIEC
update_customer_reniec_data(dni: str, reniec_data: Dict[str, Any])
```

### 2. ReniecService (`reniec_service.py`)
Modificación del método `consultar_dni`:
- **Paso 1**: Verifica en BD local
- **Paso 2**: Si existe, retorna datos locales
- **Paso 3**: Si no existe, consulta API externa
- **Paso 4**: Guarda respuesta en BD para futuras consultas

### 3. Schemas (`schemas.py`)
Agregado campo opcional en `ReniecDNIResponse`:
- `source`: Indica si los datos vinieron de 'database' o 'api'

### 4. Routes (`reniec.py`)
Actualizado para incluir el campo `source` en la respuesta

## Aplicar los Cambios

### 1. Aplicar Migración
```bash
cd /home/luis/Project/supabase

# Aplicar migración en Supabase local (si usas Docker)
supabase db push

# O aplicar en producción
supabase db push --db-url postgresql://[connection-string]
```

### 2. Reiniciar el Backend
```bash
cd /home/luis/Project/IMEI

# Si usas Railway o similar, hacer deploy
# Si es local:
python main.py
```

## Configuración

Los datos de RENIEC son estáticos y se mantienen permanentemente en cache. Una vez consultados, se reutilizan indefinidamente sin necesidad de revalidación.

## Beneficios

1. **Reducción de Costos**: Menos llamadas a API externa
2. **Mejor Performance**: Respuestas más rápidas desde BD local
3. **Datos Históricos**: Se mantiene registro de todas las consultas
4. **Resiliencia**: Si la API externa falla, se pueden usar datos del cache
5. **Trazabilidad**: El campo `source` indica de dónde vienen los datos

## Monitoreo

Los logs ahora incluyen información sobre la fuente de datos:
- `🔍 Verificando DNI en base de datos local...`
- `✅ Datos encontrados en BD para DNI`
- `🌐 Consultando API externa de RENIEC`
- `💾 Guardando datos de RENIEC en BD`

## API Response

Ejemplo de respuesta con el nuevo campo `source`:
```json
{
  "first_name": "Roxana Karina",
  "first_last_name": "Delgado",
  "second_last_name": "Cuellar",
  "full_name": "Delgado Cuellar Roxana Karina",
  "document_number": "46027896",
  "source": "database"  // Nuevo campo
}
```

## Testing

Para probar la implementación:

1. **Primera consulta** (debería usar API):
```bash
curl -X GET "http://localhost:8000/reniec/dni?numero=46027896"
# Verifica que source = "api"
```

2. **Segunda consulta** (debería usar BD):
```bash
curl -X GET "http://localhost:8000/reniec/dni?numero=46027896"
# Verifica que source = "database"
```

## Notas Importantes

- Los datos existentes en `customers` no se ven afectados
- La columna `name` se mantiene sin cambios
- El campo `phone` sigue siendo opcional (puede ser NULL)
- Los datos de RENIEC se reutilizan permanentemente (no caducan)

## Próximos Pasos (Opcional)

1. Agregar endpoint para forzar actualización de datos
2. Implementar bulk update para refrescar datos obsoletos
3. Agregar estadísticas de uso del cache
4. Dashboard para visualizar hits/misses del cache
