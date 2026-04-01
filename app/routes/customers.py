"""
Customers Routes - Endpoints para gestión de clientes
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas import CustomerListResponse, ErrorResponse
from app.services.supabase_service import SupabaseService
from app.middleware.auth_middleware import get_current_user, UserInfo

logger = logging.getLogger(__name__)

router = APIRouter()
supabase_service = SupabaseService()


@router.get(
    "/",
    response_model=CustomerListResponse,
    summary="Listar clientes",
    responses={
        200: {"description": "Lista de clientes obtenida correctamente"},
        500: {"model": ErrorResponse, "description": "Error del servidor"}
    }
)
def list_customers(
    search: Optional[str] = Query(
        default=None,
        description="Filtrar por nombre, DNI o teléfono",
        max_length=100
    ),
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Registros por página"),
    current_user: UserInfo = Depends(get_current_user)
):
    """
    Retorna la lista paginada de clientes.
    - Rol **user**: solo clientes que tengan al menos una factura del usuario autenticado con producto registrado.
    - Rol **admin**: todos los clientes de todos los usuarios con producto registrado.
    """
    try:
        # Admin ve todos; user solo los suyos
        filter_user_id = None if current_user.role == "admin" else current_user.user_id
        result = supabase_service.customers.get_all_customers(search=search, page=page, page_size=page_size, user_id=filter_user_id)

        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Error al obtener clientes'))

        return CustomerListResponse(
            success=True,
            data=result['data'],
            total=result['total'],
            page=result['page'],
            page_size=result['page_size'],
            total_pages=result['total_pages'],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en list_customers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
