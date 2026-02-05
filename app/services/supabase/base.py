"""
BaseSupabaseRepository - Clase base con cliente Singleton compartido
Todos los repositorios heredan de esta clase para reutilizar la conexión
"""

import logging
from typing import Optional
from app.config import settings

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("Instala supabase-py: pip install supabase")

logger = logging.getLogger(__name__)

# Cliente Singleton compartido por todos los repositorios
_supabase_client: Optional[Client] = None
_client_initialized: bool = False


class BaseSupabaseRepository:
    """
    Clase base para todos los repositorios de Supabase.
    Proporciona un cliente Supabase compartido (Singleton) y métodos comunes.
    """
    
    def __init__(self):
        """Inicializa el repositorio con el cliente Singleton compartido"""
        self.client: Optional[Client] = self._get_client()
    
    @staticmethod
    def _get_client() -> Optional[Client]:
        """
        Obtiene o crea el cliente Singleton de Supabase
        
        Returns:
            Cliente de Supabase o None si no hay credenciales
        """
        global _supabase_client, _client_initialized
        
        if _client_initialized:
            return _supabase_client
        
        # Intentar inicializar el cliente
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("⚠️  Credenciales de Supabase no configuradas")
            _supabase_client = None
            _client_initialized = True
            return None
        
        try:
            _supabase_client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            _client_initialized = True
            logger.info("✅ Conexión con Supabase establecida (Singleton)")
            return _supabase_client
        except Exception as e:
            logger.error(f"❌ Error al conectar con Supabase: {str(e)}")
            _supabase_client = None
            _client_initialized = True
            return None
    
    def is_connected(self) -> bool:
        """
        Verifica si el cliente está conectado a Supabase
        
        Returns:
            True si hay conexión activa, False en caso contrario
        """
        if self.client is not None:
            return True
        
        # Reintentar obtener el cliente (en caso de reconexión)
        self.client = self._get_client()
        return self.client is not None
    
    @staticmethod
    def reset_connection():
        """
        Reinicia la conexión Singleton (útil para testing o reconexión)
        ⚠️  Usar con precaución en producción
        """
        global _supabase_client, _client_initialized
        _supabase_client = None
        _client_initialized = False
        logger.warning("🔄 Conexión Singleton reiniciada")
