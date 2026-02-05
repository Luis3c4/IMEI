"""
DeviceRepository - Gestión de dispositivos y historial de consultas
Maneja las tablas: devices, consulta_history
"""

import logging
from typing import Dict, Any
from .base import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class DeviceRepository(BaseSupabaseRepository):
    """Repositorio para operaciones relacionadas con dispositivos"""
    
    # ==================== TABLA: DEVICES ====================
    
    def insert_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserta un nuevo dispositivo en la BD
        
        Args:
            device_data: Diccionario con datos del dispositivo
            
        Returns:
            Dict con success, data o error
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table('devices').insert(
                device_data
            ).execute()
            
            logger.info(f"✅ Dispositivo insertado: {device_data.get('imei')}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al insertar dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_device(self, imei: str) -> Dict[str, Any]:
        """
        Obtiene un dispositivo por IMEI
        
        Args:
            imei: IMEI del dispositivo
            
        Returns:
            Dict con success, data o error
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table('devices').select(
                "*"
            ).eq("imei", imei).execute()
            
            if response.data:
                return {'success': True, 'data': response.data[0]}
            return {'success': False, 'error': 'Dispositivo no encontrado'}
        except Exception as e:
            logger.error(f"❌ Error al obtener dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_device(self, imei: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un dispositivo existente
        
        Args:
            imei: IMEI del dispositivo a actualizar
            device_data: Datos a actualizar
            
        Returns:
            Dict con success, data o error
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table('devices').update(
                device_data
            ).eq("imei", imei).execute()
            
            logger.info(f"✅ Dispositivo actualizado: {imei}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al actualizar dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def list_devices(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        Lista dispositivos con paginación
        
        Args:
            limit: Número máximo de resultados (default: 100)
            offset: Offset para paginación (default: 0)
            
        Returns:
            Dict con success, data (lista) o error
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table('devices').select(
                "*"
            ).range(offset, offset + limit - 1).execute()
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al listar dispositivos: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}
    
    # ==================== TABLA: CONSULTA_HISTORY ====================
    
    def insert_history(self, history_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inserta un registro de consulta en el historial
        
        Args:
            history_data: Datos de la consulta a registrar
            
        Returns:
            Dict con success, data o error
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table('consulta_history').insert(
                history_data
            ).execute()
            
            logger.info(f"✅ Consulta registrada: {history_data.get('imei')}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al registrar consulta: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_device_history(self, imei: str, limit: int = 50) -> Dict[str, Any]:
        """
        Obtiene el historial de consultas de un dispositivo
        
        Args:
            imei: IMEI del dispositivo
            limit: Número máximo de registros (default: 50)
            
        Returns:
            Dict con success, data (lista ordenada por fecha desc) o error
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table('consulta_history').select(
                "*"
            ).eq("imei", imei).order("created_at", desc=True).limit(limit).execute()
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al obtener historial: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}
