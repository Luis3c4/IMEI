# 🚀 Guía de Instalación y Configuración de Supabase

## Paso 1: Obtener Credenciales de Supabase

1. Ve a [supabase.com](https://supabase.com)
2. Inicia sesión o crea una cuenta
3. Crea un nuevo proyecto (o usa uno existente)
4. En tu proyecto, ve a **Settings → API**
5. Copia:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`

## Paso 2: Actualizar Variables de Entorno

Edita tu archivo `.env` y agrega:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# Los nombres de las tablas se definen en el código fuente como literales.
```

## Paso 3: Crear Tablas en Supabase

En Supabase, abre el **SQL Editor** y ejecuta:

### Tabla de Dispositivos
```sql
CREATE TABLE devices (
  id BIGSERIAL PRIMARY KEY,
  imei VARCHAR(255) UNIQUE NOT NULL,
  marca VARCHAR(100),
  modelo VARCHAR(100),
  estado VARCHAR(50),
  fecha_consulta TIMESTAMP,
  datos_adicionales JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_imei ON devices(imei);
```

### Tabla de Historial
```sql
CREATE TABLE consulta_history (
  id BIGSERIAL PRIMARY KEY,
  imei VARCHAR(255) NOT NULL,
  resultado VARCHAR(50),
  fecha_consulta TIMESTAMP,
  ip_origen VARCHAR(45),
  usuario VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_imei_history ON consulta_history(imei);
CREATE INDEX idx_fecha ON consulta_history(fecha_consulta);
```

## Paso 4: Activar Row Level Security (RLS) - Opcional

Para mayor seguridad, habilita RLS:

```sql
-- Tabla devices
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public select" ON devices
  FOR SELECT USING (true);

CREATE POLICY "Allow authenticated insert" ON devices
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Tabla consulta_history
ALTER TABLE consulta_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public select" ON consulta_history
  FOR SELECT USING (true);

CREATE POLICY "Allow authenticated insert" ON consulta_history
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');
```

## Paso 5: Usar el Servicio en Tu Aplicación

### Opción A: En una ruta FastAPI

```python
from fastapi import APIRouter
from app.services.supabase_service import supabase_service
from app.schemas import QueryDeviceRequest, QueryDeviceResponse

router = APIRouter()

@router.post("/guardar-dispositivo")
async def guardar_dispositivo(request: QueryDeviceRequest):
    """Guarda un dispositivo en Supabase"""
    
    device_data = {
        "imei": request.input_value,
        "marca": "Apple",
        "estado": "Activo",
        "fecha_consulta": datetime.now().isoformat()
    }
    
    result = await supabase_service.save_device(device_data)
    
    if result['success']:
        return {"success": True, "message": "Dispositivo guardado"}
    else:
        raise HTTPException(status_code=400, detail=result['error'])
```

### Opción B: Script independiente

```python
import asyncio
from app.services.supabase_service import supabase_service

async def main():
    # Obtener dispositivos
    result = await supabase_service.get_devices(limit=50)
    
    if result['success']:
        devices = result['data']
        for device in devices:
            print(f"IMEI: {device['imei']}, Marca: {device['marca']}")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Métodos Disponibles

### Lectura
- `get_devices(limit=100)` - Obtiene dispositivos
- `get_device_by_imei(imei)` - Obtiene dispositivo específico
- `get_query_history(imei, limit=50)` - Obtiene historial

### Escritura
- `save_device(device_data)` - Crea dispositivo
- `update_device(imei, data)` - Actualiza dispositivo
- `delete_device(imei)` - Elimina dispositivo
- `save_query_history(history_data)` - Registra consulta

### Generales
- `insert_record(table, data)` - Inserta en tabla
- `get_records(table, filters={}, limit=100)` - Lee registros
- `update_record(table, id_column, id_value, data)` - Actualiza
- `delete_record(table, id_column, id_value)` - Elimina

## Pruebas

Ejecuta el archivo de ejemplos:

```bash
source venv/bin/activate
python3 examples_supabase.py
```

## Solución de Problemas

### "Supabase no está conectado"
- Verifica que `SUPABASE_URL` y `SUPABASE_KEY` están en `.env`
- Reinicia la aplicación después de cambiar `.env`

### Error de conexión
- Verifica que el `SUPABASE_URL` es correcto (sin `/` al final)
- Comprueba que la clave es válida en Settings → API

### Error de permisos
- Habilita RLS con políticas públicas (ver Paso 4)
- O desactiva RLS temporalmente en Settings → Auth

### Tabla no existe
- Asegúrate de que el nombre en `.env` coincide con la tabla
- Verifica que ejecutaste el SQL para crear las tablas

## Próximos Pasos

1. Integra Supabase en tus rutas existentes
2. Configura respaldos automáticos en Supabase
3. Monitorea el uso en Settings → Database
4. Considera usar Auth de Supabase para usuarios
