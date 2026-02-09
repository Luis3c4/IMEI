"""
Authentication Middleware for FastAPI
Validates Supabase JWT tokens and injects user_id into request context
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("Instala supabase-py: pip install supabase")

logger = logging.getLogger(__name__)

# HTTPBearer security scheme
security = HTTPBearer()

# Cliente Supabase para validación de tokens (usa anon key, no service role)
_auth_client: Optional[Client] = None


def _get_auth_client() -> Client:
    """
    Obtiene o crea el cliente de Supabase para autenticación
    Usa la anon key (no la service role key) para validar JWT tokens
    
    Returns:
        Cliente de Supabase configurado para autenticación
        
    Raises:
        HTTPException: Si las credenciales de Supabase no están configuradas
    """
    global _auth_client
    
    if _auth_client is not None:
        return _auth_client
    
    if not settings.SUPABASE_URL:
        logger.error("❌ SUPABASE_URL no configurada")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuración de autenticación no disponible"
        )
    
    # Usar SUPABASE_ANON_KEY si está disponible, si no usar SUPABASE_KEY
    # (NOTA: SUPABASE_KEY es service role, idealmente deberías usar anon key)
    auth_key = getattr(settings, 'SUPABASE_ANON_KEY', None) or settings.SUPABASE_KEY
    
    if not auth_key:
        logger.error("❌ SUPABASE_ANON_KEY o SUPABASE_KEY no configuradas")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuración de autenticación no disponible"
        )
    
    try:
        _auth_client = create_client(settings.SUPABASE_URL, auth_key)
        logger.info("✅ Cliente de autenticación Supabase inicializado")
        return _auth_client
    except Exception as e:
        logger.error(f"❌ Error al inicializar cliente de autenticación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al inicializar autenticación"
        )


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Dependency de FastAPI para obtener el user_id del usuario autenticado
    
    Extrae el JWT token del header Authorization, lo valida con Supabase,
    y retorna el user_id (UUID) del usuario autenticado.
    
    Args:
        request: Request object de FastAPI
        credentials: Credenciales extraídas del header Authorization: Bearer <token>
        
    Returns:
        UUID del usuario autenticado como string
        
    Raises:
        HTTPException 401: Si el token no existe, es inválido, o ha expirado
        HTTPException 500: Si hay un error en la configuración del servidor
        
    Usage:
        @router.post("/protected-route")
        async def protected_route(user_id: str = Depends(get_current_user_id)):
            # user_id contiene el UUID del usuario autenticado
            ...
    """
    if not credentials:
        logger.warning("⚠️  No se proporcionó token de autenticación")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado: token de autenticación requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    if not token:
        logger.warning("⚠️  Token de autenticación vacío")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado: token de autenticación inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Obtener cliente de autenticación
        auth_client = _get_auth_client()
        
        # Validar el token con Supabase usando el parámetro jwt
        # El método get_user(jwt=token) valida el JWT y retorna la información del usuario
        response = auth_client.auth.get_user(jwt=token)
        
        if not response or not response.user:
            logger.warning("⚠️  Token inválido o usuario no encontrado")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No autorizado: token inválido o expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = response.user.id
        
        if not user_id:
            logger.error("❌ Usuario autenticado pero sin ID")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error en la autenticación: usuario sin ID"
            )
        
        # Inyectar user_id en el contexto de la request (opcional, útil para logging)
        request.state.user_id = user_id
        
        logger.info(f"✅ Usuario autenticado: {user_id}")
        return user_id
        
    except HTTPException:
        # Re-lanzar excepciones HTTP ya formateadas
        raise
    except Exception as e:
        # Capturar cualquier otro error no esperado
        logger.error(f"❌ Error al validar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error al validar token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
