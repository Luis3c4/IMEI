"""
Servicio para manejar todas las interacciones con Supabase
Base de datos PostgreSQL con API REST/GraphQL
"""

import logging
from typing import Dict, Any, List, Optional
from ..config import settings

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("Instala supabase-py: pip install supabase")

logger = logging.getLogger(__name__)


class SupabaseService:
    """Servicio para manejar operaciones con Supabase"""
    
    def __init__(self):
        """Inicializa la conexión con Supabase"""
        self.client: Optional[Client] = None
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("⚠️  Credenciales de Supabase no configuradas")
            return
        
        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("✅ Conexión con Supabase establecida")
        except Exception as e:
            logger.error(f"❌ Error al conectar con Supabase: {str(e)}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Verifica si está conectado a Supabase"""
        return self.client is not None
    
    # ==================== TABLA: DEVICES ====================
    
    def insert_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inserta un nuevo dispositivo en la BD"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table(settings.SUPABASE_TABLE_DEVICES).insert(
                device_data
            ).execute()
            
            logger.info(f"✅ Dispositivo insertado: {device_data.get('imei')}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al insertar dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_device(self, imei: str) -> Dict[str, Any]:
        """Obtiene un dispositivo por IMEI"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table(settings.SUPABASE_TABLE_DEVICES).select(
                "*"
            ).eq("imei", imei).execute()
            
            if response.data:
                return {'success': True, 'data': response.data[0]}
            return {'success': False, 'error': 'Dispositivo no encontrado'}
        except Exception as e:
            logger.error(f"❌ Error al obtener dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_device(self, imei: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un dispositivo"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table(settings.SUPABASE_TABLE_DEVICES).update(
                device_data
            ).eq("imei", imei).execute()
            
            logger.info(f"✅ Dispositivo actualizado: {imei}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al actualizar dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def list_devices(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Lista todos los dispositivos"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table(settings.SUPABASE_TABLE_DEVICES).select(
                "*"
            ).range(offset, offset + limit - 1).execute()
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al listar dispositivos: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}
    
    # ==================== TABLA: CONSULTA_HISTORY ====================
    
    def insert_history(self, history_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inserta un registro de consulta en el historial"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table(settings.SUPABASE_TABLE_HISTORY).insert(
                history_data
            ).execute()
            
            logger.info(f"✅ Consulta registrada: {history_data.get('imei')}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al registrar consulta: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_device_history(self, imei: str, limit: int = 50) -> Dict[str, Any]:
        """Obtiene el historial de consultas de un dispositivo"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table(settings.SUPABASE_TABLE_HISTORY).select(
                "*"
            ).eq("imei", imei).order("created_at", desc=True).limit(limit).execute()
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al obtener historial: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}
    
    # ==================== OPERACIONES GENÉRICAS ====================
    
    def raw_query(self, table: str, operation: str = "select", **kwargs) -> Dict[str, Any]:
        """Ejecuta una operación genérica en una tabla"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            if operation == "select":
                response = self.client.table(table).select(kwargs.get("columns", "*")).execute()  # type: ignore
            elif operation == "insert":
                response = self.client.table(table).insert(kwargs.get("data", {})).execute()  # type: ignore
            elif operation == "update":
                response = self.client.table(table).update(kwargs.get("data", {})).execute()  # type: ignore
            elif operation == "delete":
                response = self.client.table(table).delete().execute()  # type: ignore
            else:
                return {'success': False, 'error': f'Operación no soportada: {operation}'}
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error en operación {operation}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ==================== TABLA: PRODUCTS ==================== 
    def get_products_with_variants(self) -> Dict[str, Any]:
        """Obtiene todos los productos con sus variantes (JOIN)"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table('products').select(
                """
                *,
                product_variants (
                    id,
                    color,
                    capacity,
                    serial_number,
                    price,
                    quantity,
                    created_at,
                    updated_at
                )
                """
            ).execute()
            
            logger.info(f"✅ Productos con variantes obtenidos: {len(response.data)} productos")
            return {'success': True, 'data': response.data, 'count': len(response.data)}
        except Exception as e:
            logger.error(f"❌ Error al obtener productos con variantes: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}

# Instancia global del servicio
supabase_service = SupabaseService()
