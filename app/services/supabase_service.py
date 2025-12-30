"""
<<<<<<< HEAD
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
=======
Supabase Service
Maneja la conexión y operaciones con Supabase
"""

import logging
from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from app.config import settings
>>>>>>> 3a14677 (configurando supabase)

logger = logging.getLogger(__name__)


class SupabaseService:
<<<<<<< HEAD
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
    
    def get_all_products(self) -> Dict[str, Any]:
        """Obtiene todos los productos de la tabla products"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table(settings.SUPABASE_TABLE_PRODUCTS).select(
                "*"
            ).execute()
            
            logger.info(f"✅ Productos obtenidos: {len(response.data)} productos")
            return {'success': True, 'data': response.data, 'count': len(response.data)}
        except Exception as e:
            logger.error(f"❌ Error al obtener productos: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}
=======
    """Servicio para interactuar con Supabase"""
    
    _instance: Optional['SupabaseService'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        """Patrón Singleton para asegurar una única conexión"""
        if cls._instance is None:
            cls._instance = super(SupabaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa la conexión con Supabase"""
        if self._client is None and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self._client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("✅ Conexión con Supabase establecida correctamente")
            except Exception as e:
                logger.error(f"❌ Error al conectar con Supabase: {str(e)}")
                self._client = None
    
    def is_connected(self) -> bool:
        """Verifica si la conexión con Supabase está activa"""
        return self._client is not None
    
    def get_client(self) -> Optional[Client]:
        """Retorna el cliente de Supabase"""
        return self._client
    
    # ============ OPERACIONES CRUD ============
    
    async def insert_record(
        self,
        table: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Inserta un registro en una tabla
        
        Args:
            table: Nombre de la tabla
            data: Datos a insertar
            
        Returns:
            Respuesta de Supabase
        """
        try:
            if not self.is_connected():
                return {'success': False, 'error': 'Supabase no está conectado'}
            
            response = self._client.table(table).insert(data).execute()
            logger.info(f"✅ Registro insertado en {table}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al insertar en {table}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_records(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Obtiene registros de una tabla
        
        Args:
            table: Nombre de la tabla
            filters: Filtros a aplicar (diccionario key=value)
            limit: Límite de registros
            
        Returns:
            Lista de registros
        """
        try:
            if not self.is_connected():
                return {'success': False, 'error': 'Supabase no está conectado'}
            
            query = self._client.table(table).select("*")
            
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            
            response = query.limit(limit).execute()
            logger.info(f"✅ {len(response.data)} registros obtenidos de {table}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al obtener registros de {table}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_record_by_id(
        self,
        table: str,
        id_column: str,
        id_value: Any
    ) -> Dict[str, Any]:
        """
        Obtiene un registro específico por ID
        
        Args:
            table: Nombre de la tabla
            id_column: Nombre de la columna ID
            id_value: Valor del ID
            
        Returns:
            Registro encontrado
        """
        try:
            if not self.is_connected():
                return {'success': False, 'error': 'Supabase no está conectado'}
            
            response = self._client.table(table).select("*").eq(id_column, id_value).execute()
            
            if response.data:
                logger.info(f"✅ Registro encontrado en {table}")
                return {'success': True, 'data': response.data[0]}
            else:
                return {'success': False, 'error': 'Registro no encontrado', 'data': None}
        except Exception as e:
            logger.error(f"❌ Error al obtener registro de {table}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def update_record(
        self,
        table: str,
        id_column: str,
        id_value: Any,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Actualiza un registro
        
        Args:
            table: Nombre de la tabla
            id_column: Nombre de la columna ID
            id_value: Valor del ID
            data: Datos a actualizar
            
        Returns:
            Respuesta de Supabase
        """
        try:
            if not self.is_connected():
                return {'success': False, 'error': 'Supabase no está conectado'}
            
            response = self._client.table(table).update(data).eq(id_column, id_value).execute()
            logger.info(f"✅ Registro actualizado en {table}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al actualizar en {table}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def delete_record(
        self,
        table: str,
        id_column: str,
        id_value: Any
    ) -> Dict[str, Any]:
        """
        Elimina un registro
        
        Args:
            table: Nombre de la tabla
            id_column: Nombre de la columna ID
            id_value: Valor del ID
            
        Returns:
            Respuesta de Supabase
        """
        try:
            if not self.is_connected():
                return {'success': False, 'error': 'Supabase no está conectado'}
            
            response = self._client.table(table).delete().eq(id_column, id_value).execute()
            logger.info(f"✅ Registro eliminado de {table}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al eliminar de {table}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ============ OPERACIONES DE DISPOSITIVOS ============
    
    async def save_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda un dispositivo en Supabase"""
        return await self.insert_record(settings.SUPABASE_TABLE_DEVICES, device_data)
    
    async def get_devices(self, limit: int = 100) -> Dict[str, Any]:
        """Obtiene todos los dispositivos"""
        return await self.get_records(settings.SUPABASE_TABLE_DEVICES, limit=limit)
    
    async def get_device_by_imei(self, imei: str) -> Dict[str, Any]:
        """Obtiene un dispositivo por IMEI"""
        return await self.get_record_by_id(
            settings.SUPABASE_TABLE_DEVICES,
            "imei",
            imei
        )
    
    async def update_device(self, imei: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un dispositivo"""
        return await self.update_record(
            settings.SUPABASE_TABLE_DEVICES,
            "imei",
            imei,
            data
        )
    
    async def delete_device(self, imei: str) -> Dict[str, Any]:
        """Elimina un dispositivo"""
        return await self.delete_record(
            settings.SUPABASE_TABLE_DEVICES,
            "imei",
            imei
        )
    
    # ============ OPERACIONES DE HISTORIAL ============
    
    async def save_query_history(self, history_data: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda un registro de consulta"""
        return await self.insert_record(settings.SUPABASE_TABLE_HISTORY, history_data)
    
    async def get_query_history(self, imei: str, limit: int = 50) -> Dict[str, Any]:
        """Obtiene el historial de consultas de un dispositivo"""
        return await self.get_records(
            settings.SUPABASE_TABLE_HISTORY,
            filters={'imei': imei},
            limit=limit
        )
>>>>>>> 3a14677 (configurando supabase)


# Instancia global del servicio
supabase_service = SupabaseService()
