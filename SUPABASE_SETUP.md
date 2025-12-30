# 📚 Guía de Integración con Supabase

## 1️⃣ Estructura de Carpetas Recomendada

```
app/
├── services/
│   ├── supabase_service.py    ← Cliente Supabase
│   ├── dhru_service.py
│   └── sheets_service.py
├── routes/
│   └── devices.py              ← Usa supabase_service
├── schemas.py
└── config.py
```

## 2️⃣ Pasos de Configuración

### A) Crear Proyecto Supabase

1. Ir a [supabase.com](https://supabase.com)
2. Crear nuevo proyecto
3. Copiar credenciales:
   - `SUPABASE_URL` → URL del proyecto
   - `SUPABASE_KEY` → Clave anón (Configuración > API)

### B) Configurar Variables de Entorno

```bash
# Crear/Editar archivo .env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=eyJhbGc... (tu clave anon)
```

### C) Instalar Dependencias

```bash
pip install -r requirements.txt
```

### D) Crear Tablas en Supabase

1. Ir a SQL Editor en Dashboard de Supabase
2. Copiar y ejecutar el SQL de [scripts/init_supabase.py](../scripts/init_supabase.py)

## 3️⃣ Uso en tu Código

### Ejemplo: Guardar Dispositivo Consultado

```python
from app.services.supabase_service import supabase_service
from app.services.dhru_service import DHRUService

@router.post("/query")
async def query_device(imei: str):
    # 1. Consultar DHRU API
    dhru = DHRUService()
    result = dhru.query_device("tu_service_id", imei)
    
    # 2. Guardar en Supabase
    supabase_service.insert_device({
        "imei": imei,
        "device_name": result.get("device_name"),
        "brand": result.get("brand"),
        "model": result.get("model"),
        "status": "active"
    })
    
    # 3. Registrar en historial
    supabase_service.insert_history({
        "imei": imei,
        "query_result": result,
        "status": "success"
    })
    
    return result
```

### Ejemplo: Obtener Historial

```python
@router.get("/devices/{imei}/history")
async def get_device_history(imei: str, limit: int = 50):
    result = supabase_service.get_device_history(imei, limit)
    return result
```

## 4️⃣ Métodos Disponibles

### CRUD Dispositivos
- `supabase_service.insert_device(data)` - Crear
- `supabase_service.get_device(imei)` - Obtener uno
- `supabase_service.update_device(imei, data)` - Actualizar
- `supabase_service.list_devices(limit, offset)` - Listar todos

### Historial
- `supabase_service.insert_history(data)` - Registrar consulta
- `supabase_service.get_device_history(imei, limit)` - Obtener historial

### Validación
- `supabase_service.is_connected()` - Verificar conexión

## 5️⃣ Estructura de Datos

### Tabla: devices
```
id             → BIGINT (auto)
imei           → TEXT (UNIQUE)
device_name    → TEXT
brand          → TEXT
model          → TEXT
status         → TEXT ('active', 'inactive', etc)
last_query     → TIMESTAMP
created_at     → TIMESTAMP
updated_at     → TIMESTAMP
```

### Tabla: consulta_history
```
id             → BIGINT (auto)
imei           → TEXT (FK a devices.imei)
query_result   → JSONB (resultado de DHRU)
status         → TEXT ('success', 'error')
created_at     → TIMESTAMP
```

## 6️⃣ Seguridad (RLS - Row Level Security)

Para producción, habilita RLS en Supabase:

```sql
-- Políticas de ejemplo
CREATE POLICY "Allow read all" ON devices
  FOR SELECT USING (true);

CREATE POLICY "Allow insert with api key" ON devices
  FOR INSERT WITH CHECK (true);
```

## 7️⃣ Troubleshooting

| Problema | Solución |
|----------|----------|
| "Supabase no conectado" | Verifica SUPABASE_URL y SUPABASE_KEY en .env |
| "Tabla no existe" | Ejecuta el SQL en Supabase > SQL Editor |
| "Permiso denegado" | Revisa RLS policies en Supabase Dashboard |
| Error de import | Instala: `pip install supabase` |

## 📌 Próximas Integraciones Sugeridas

- [ ] Agregar autenticación con Supabase Auth
- [ ] Implementar caché con Redis
- [ ] Configurar backups automáticos
- [ ] Monitoreo de queries con PostgREST
