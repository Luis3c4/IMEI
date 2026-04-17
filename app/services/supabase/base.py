"""
BaseSupabaseRepository - Clase base con cliente Singleton compartido (Async)
Todos los repositorios heredan de esta clase para reutilizar la conexión
"""

import asyncio
import logging
from typing import Optional
from app.config import settings

try:
    from supabase import acreate_client, AsyncClient
except ImportError:
    raise ImportError("Instala supabase-py: pip install supabase")

logger = logging.getLogger(__name__)

# Cliente Singleton compartido por todos los repositorios
_supabase_client: Optional[AsyncClient] = None
_client_initialized: bool = False
_client_lock: asyncio.Lock | None = None


def _get_lock() -> asyncio.Lock:
    """Obtiene o crea el lock para inicialización thread-safe del cliente"""
    global _client_lock
    if _client_lock is None:
        _client_lock = asyncio.Lock()
    return _client_lock


class BaseSupabaseRepository:
    """
    Clase base para todos los repositorios de Supabase.
    Proporciona un cliente AsyncClient compartido (Singleton) y métodos comunes.
    El cliente se inicializa de forma lazy en la primera llamada async.
    """

    @staticmethod
    async def _get_client() -> Optional[AsyncClient]:
        """
        Obtiene o crea el cliente async Singleton de Supabase
        
        Returns:
            AsyncClient de Supabase o None si no hay credenciales
        """
        global _supabase_client, _client_initialized
        
        if _client_initialized:
            return _supabase_client
        
        async with _get_lock():
            # Double-check después de adquirir el lock
            if _client_initialized:
                return _supabase_client
            
            # Intentar inicializar el cliente
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                logger.warning("⚠️  Credenciales de Supabase no configuradas")
                _supabase_client = None
                _client_initialized = True
                return None
            
            try:
                _supabase_client = await acreate_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                _client_initialized = True
                logger.info("✅ Conexión async con Supabase establecida (Singleton)")
                return _supabase_client
            except Exception as e:
                logger.error(f"❌ Error al conectar con Supabase: {str(e)}")
                _supabase_client = None
                _client_initialized = True
                return None
    
    async def is_connected(self) -> bool:
        """
        Verifica si el cliente está conectado a Supabase
        
        Returns:
            True si hay conexión activa, False en caso contrario
        """
        client = await self._get_client()
        return client is not None
    
    @staticmethod
    def reset_connection():
        """
        Reinicia la conexión Singleton (útil para testing o reconexión)
        ⚠️  Usar con precaución en producción
        """
        global _supabase_client, _client_initialized, _client_lock
        _supabase_client = None
        _client_initialized = False
        _client_lock = None
        logger.warning("🔄 Conexión Singleton reiniciada")
