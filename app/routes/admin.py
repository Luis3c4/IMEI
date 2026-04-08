"""
Admin Routes - Gestión de usuarios y roles
Solo accesible por usuarios con rol 'admin'
"""

import logging
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.middleware.auth_middleware import require_admin
from app.config import settings

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("Instala supabase-py: pip install supabase")

logger = logging.getLogger(__name__)

router = APIRouter()

# Cliente con service role key para operaciones de administración
_admin_client: Client | None = None


def _get_admin_client() -> Client:
    global _admin_client
    if _admin_client is not None:
        return _admin_client

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuración de Supabase no disponible"
        )

    _admin_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _admin_client


class UpdateRoleRequest(BaseModel):
    role: Literal["admin", "user"]


@router.patch(
    "/users/{user_id}/role",
    summary="Actualizar rol de usuario",
    responses={
        200: {"description": "Rol actualizado correctamente"},
        403: {"description": "Acceso denegado: se requiere rol admin"},
        404: {"description": "Usuario no encontrado"},
        500: {"description": "Error del servidor"},
    }
)
def update_user_role(
    user_id: str,
    body: UpdateRoleRequest,
    _: None = Depends(require_admin),
):
    """
    Actualiza el rol de un usuario en app_metadata.
    Solo accesible por administradores.

    - **user_id**: UUID del usuario a actualizar
    - **role**: `admin` o `user`
    """
    try:
        admin_client = _get_admin_client()
        response = admin_client.auth.admin.update_user_by_id(
            user_id,
            {"app_metadata": {"role": body.role}}
        )

        if not response.user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        logger.info(f"✅ Rol de usuario {user_id} actualizado a '{body.role}'")
        return {
            "success": True,
            "user_id": user_id,
            "role": body.role,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error actualizando rol de usuario {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar rol: {str(e)}")


@router.get(
    "/users",
    summary="Listar usuarios con sus roles",
    responses={
        200: {"description": "Lista de usuarios obtenida correctamente"},
        403: {"description": "Acceso denegado: se requiere rol admin"},
        500: {"description": "Error del servidor"},
    }
)
def list_users(_: None = Depends(require_admin)):
    """
    Devuelve todos los usuarios con su id, email, nombre y rol actual.
    Solo accesible por administradores.
    """
    try:
        admin_client = _get_admin_client()
        response = admin_client.auth.admin.list_users()

        users = []
        for u in response:
            users.append({
                "id": u.id,
                "email": u.email,
                "name": (u.user_metadata or {}).get("name", ""),
                "role": (u.app_metadata or {}).get("role", "user"),
                "created_at": str(u.created_at),
            })

        return {"success": True, "data": users, "total": len(users)}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listando usuarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al listar usuarios: {str(e)}")
