"""
Ejemplo de uso del servicio de Supabase
Demuestra cómo usar las funciones básicas
"""

import asyncio
import logging
from app.services.supabase_service import supabase_service
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Ejecuta ejemplos de uso del servicio Supabase"""
    
    # Verificar conexión
    if not supabase_service.is_connected():
        logger.error("❌ Supabase no está conectado. Verifica SUPABASE_URL y SUPABASE_KEY en .env")
        return
    
    logger.info("✅ Supabase conectado correctamente")
    
    # Ejemplo 1: Guardar un dispositivo
    logger.info("\n Ejemplo 1: Guardar un dispositivo")
    device_data = {
        "imei": "123456789012345",
        "marca": "Apple",
        "modelo": "iPhone 12",
        "estado": "Activo",
        "fecha_consulta": datetime.now().isoformat(),
        "datos_adicionales": {"color": "Negro", "almacenamiento": "128GB"}
    }
    result = await supabase_service.save_device(device_data)
    logger.info(f"Resultado: {result}")
    
    # Ejemplo 2: Obtener dispositivos
    logger.info("\n📖 Ejemplo 2: Obtener dispositivos")
    result = await supabase_service.get_devices(limit=10)
    if result['success']:
        logger.info(f"Se encontraron {len(result['data'])} dispositivos")
    else:
        logger.warning(f"Error: {result['error']}")
    
    # Ejemplo 3: Obtener dispositivo por IMEI
    logger.info("\n🔍 Ejemplo 3: Obtener dispositivo por IMEI")
    result = await supabase_service.get_device_by_imei("123456789012345")
    if result['success']:
        logger.info(f"Dispositivo encontrado: {result['data']}")
    else:
        logger.warning(f"Error o no encontrado: {result.get('error')}")
    
    # Ejemplo 4: Actualizar dispositivo
    logger.info("\n✏️ Ejemplo 4: Actualizar dispositivo")
    update_data = {
        "estado": "Inactivo",
        "fecha_ultima_actualizacion": datetime.now().isoformat()
    }
    result = await supabase_service.update_device("123456789012345", update_data)
    logger.info(f"Resultado: {result}")
    
    # Ejemplo 5: Guardar historial de consulta
    logger.info("\n📚 Ejemplo 5: Guardar historial de consulta")
    history_data = {
        "imei": "123456789012345",
        "resultado": "Activo",
        "fecha_consulta": datetime.now().isoformat(),
        "ip_origen": "192.168.1.1",
        "usuario": "test_user"
    }
    result = await supabase_service.save_query_history(history_data)
    logger.info(f"Resultado: {result}")
    
    # Ejemplo 6: Obtener historial
    logger.info("\n📖 Ejemplo 6: Obtener historial de un dispositivo")
    result = await supabase_service.get_query_history("123456789012345", limit=5)
    if result['success']:
        logger.info(f"Se encontraron {len(result['data'])} registros de historial")
    else:
        logger.warning(f"Error: {result['error']}")
    
    # Ejemplo 7: Eliminar dispositivo
    logger.info("\n🗑️ Ejemplo 7: Eliminar dispositivo")
    result = await supabase_service.delete_device("123456789012345")
    logger.info(f"Resultado: {result}")


if __name__ == "__main__":
    asyncio.run(main())
