"""
Rutas para el historial de ventas (Quantum).
Retorna todas las facturas con datos anidados de cliente y productos
para poblar la tabla de historial en el frontend.
"""
from fastapi import APIRouter, HTTPException, Depends, Query

from app.services.supabase_service import supabase_service
from app.middleware import get_current_user_id

router = APIRouter()


@router.get("")
async def get_historial(
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Registros por página"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Retorna el historial de ventas paginado: facturas con sus productos,
    variantes, items (serial) y datos del cliente.

    Cada factura puede tener múltiples invoice_products.
    El frontend los expande en filas individuales.
    """
    try:
        result = await supabase_service.invoices.get_historial_invoices(
            page=page, page_size=page_size
        )

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error al obtener historial: {result.get('error', 'Error desconocido')}",
            )

        return {
            "success": True,
            "data": result["data"],
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en historial: {str(e)}")
