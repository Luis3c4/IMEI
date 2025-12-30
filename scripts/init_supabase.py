"""
Script de inicialización de Supabase
Crea las tablas necesarias en tu base de datos
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path de Python
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from app.services.supabase_service import supabase_service
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def init_supabase_tables():
    """
    Inicializa las tablas en Supabase
    
    Ejecutar las siguientes sentencias SQL en tu dashboard de Supabase:
    
    -- Tabla: devices
    CREATE TABLE devices (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        imei TEXT UNIQUE NOT NULL,
        device_name TEXT,
        brand TEXT,
        model TEXT,
        status TEXT DEFAULT 'active',
        last_query TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX idx_devices_imei ON devices(imei);
    CREATE INDEX idx_devices_status ON devices(status);
    
    -- Tabla: consulta_history
    CREATE TABLE consulta_history (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        imei TEXT NOT NULL REFERENCES devices(imei),
        query_result JSONB,
        status TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE INDEX idx_history_imei ON consulta_history(imei);
    CREATE INDEX idx_history_created_at ON consulta_history(created_at);
    
    -- Habilitar RLS si necesitas seguridad
    ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
    ALTER TABLE consulta_history ENABLE ROW LEVEL SECURITY;
    """
    
    if not supabase_service.is_connected():
        print("⚠️  Supabase no está conectado. Verifica tus credenciales.")
        return False
    
    print("✅ Supabase está listo y conectado!")
    print("\n📋 INSTRUCCIONES:")
    print("Ejecuta las siguientes sentencias SQL en tu dashboard de Supabase:")
    print("https://supabase.com/dashboard/project/{tu-proyecto}/editor")
    return True


if __name__ == "__main__":
    print("🔍 Verificando conexión a Supabase...")
    init_supabase_tables()
