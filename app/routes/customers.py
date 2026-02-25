"""
Customers Routes - Endpoints para gestión de clientes
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.schemas import CustomerListResponse, ErrorResponse
from app.services.supabase_service import SupabaseService

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
async def list_customers(
    search: Optional[str] = Query(
        default=None,
        description="Filtrar por nombre, DNI o teléfono",
        max_length=100
    )
):
    """
    Retorna la lista de todos los clientes registrados.

    **Parámetros opcionales:**
    - **search** (str): Texto libre para filtrar por nombre, DNI o teléfono.

    **Respuesta:**
    - success: bool
    - data: lista de clientes con id, name, dni, phone, created_at, first_name, first_last_name, second_last_name
    - total: cantidad de resultados
    """
    try:
        result = supabase_service.customers.get_all_customers(search=search)

        if not result['success']:
            raise HTTPException(status_code=500, detail=result.get('error', 'Error al obtener clientes'))

        return CustomerListResponse(
            success=True,
            data=result['data'],
            total=result['total']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en list_customers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")
