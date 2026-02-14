"""
Rutas para manejar productos desde Supabase
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any , Optional
from pydantic import BaseModel
from app.services.supabase_service import supabase_service
from app.schemas import ProductHierarchyResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ProductsResponse(BaseModel):
    """Respuesta de productos"""
    success: bool
    data: List[Dict[str, Any]]
    count: int
    error: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    """Request para actualizar status"""
    item_id: int
    status: str


class StatusResponse(BaseModel):
    """Respuesta de actualización de status"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None


class BulkToggleRequest(BaseModel):
    """Request para toggle múltiple de items"""
    item_ids: List[int]


class BulkStatusResponse(BaseModel):
    """Respuesta de actualización múltiple de status"""
    success: bool
    total: int
    updated: int
    failed: int
    results: List[Dict[str, Any]]
    message: Optional[str] = None


@router.get("/", response_model=ProductsResponse)
async def get_all_products():
    """
    Obtiene todos los productos con sus variantes (JOIN)
    
    Returns:
        ProductsResponse: Lista de todos los productos con sus variantes
    """
    if not supabase_service.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Servicio de base de datos no disponible"
        )
    
    result = supabase_service.products.get_products_with_variants()
    
    if not result.get('success'):
        raise HTTPException(
            status_code=500,
            detail=result.get('error', 'Error al obtener productos')
        )
    
    return ProductsResponse(
        success=True,
        data=result.get('data', []),
        count=result.get('count', 0)
    )


@router.get("/health")
async def products_health():
    """
    Verifica el estado de la conexión a la base de datos
    """
    return {
        "service": "products",
        "status": "connected" if supabase_service.is_connected() else "disconnected",
        "message": "Servicio de productos operativo"
    }

@router.post("/items/bulk-toggle-sold", response_model=BulkStatusResponse)
async def bulk_toggle_items_sold(request: BulkToggleRequest):
    """
    Toggle entre available y sold para múltiples product_items
    Endpoint para manejar multiselección en el frontend
    
    Args:
        request: Objeto con la lista de item_ids a actualizar
        
    Returns:
        BulkStatusResponse con resultados de cada actualización
    """
    if not supabase_service.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Servicio de base de datos no disponible"
        )
    
    if not request.item_ids:
        raise HTTPException(
            status_code=400,
            detail="La lista de item_ids no puede estar vacía"
        )
    
    results = []
    updated_count = 0
    failed_count = 0
    
    for item_id in request.item_ids:
        try:
            # Obtener el status actual
            assert supabase_service.products.client is not None
            result = supabase_service.products.client.table('product_items').select(
                'id, status, serial_number'
            ).eq('id', item_id).execute()
            
            if not result.data or not isinstance(result.data, list) or len(result.data) == 0:
                results.append({
                    'item_id': item_id,
                    'success': False,
                    'error': 'Product item no encontrado'
                })
                failed_count += 1
                continue
            
            item_data = result.data[0]
            if not isinstance(item_data, dict):
                results.append({
                    'item_id': item_id,
                    'success': False,
                    'error': 'Datos inválidos'
                })
                failed_count += 1
                continue
            
            current_status = item_data.get('status', '')
            serial_number = item_data.get('serial_number', '')
            new_status = 'sold' if current_status == 'available' else 'available'
            
            # Actualizar status
            update_result = supabase_service.products.update_product_item_status(item_id, new_status)
            
            if update_result.get('success'):
                results.append({
                    'item_id': item_id,
                    'success': True,
                    'serial_number': serial_number,
                    'old_status': current_status,
                    'new_status': new_status
                })
                updated_count += 1
            else:
                results.append({
                    'item_id': item_id,
                    'success': False,
                    'error': update_result.get('error', 'Error desconocido')
                })
                failed_count += 1
                
        except Exception as e:
            logger.error(f"Error procesando item {item_id}: {str(e)}")
            results.append({
                'item_id': item_id,
                'success': False,
                'error': str(e)
            })
            failed_count += 1
    
    total = len(request.item_ids)
    success = failed_count == 0
    
    return BulkStatusResponse(
        success=success,
        total=total,
        updated=updated_count,
        failed=failed_count,
        results=results,
        message=f"Actualización completa: {updated_count} exitosos, {failed_count} fallidos"
    )


@router.get("/inventory", response_model=ProductHierarchyResponse)
async def get_products_inventory(
    category: Optional[str] = Query(
        default=None,
        description="Filtrar por categoría (ej: IPHONE, MACBOOK, APPLE WATCH)"
    )
):
    """
    Obtiene todo el inventario disponible con estructura jerárquica de 3 niveles.
    
    **Estructura jerárquica:**
    - **Fase 1 (Producto)**: Agrupación por producto con cantidad total, capacidades y colores
    - **Fase 2 (Capacidad)**: Agrupación por capacidad con cantidad y colores disponibles
    - **Fase 3 (Items)**: Detalles individuales con serial, product number, capacidad y color
    
    **Solo retorna items con status='available'**
    
    Args:
        category: Filtro opcional por categoría (ej: IPHONE, MACBOOK)
        
    Returns:
        ProductHierarchyResponse con todo el inventario disponible
        
    Examples:
        - `/products/inventory` - Todo el inventario
        - `/products/inventory?category=IPHONE` - Solo iPhones disponibles
    """
    if not supabase_service.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Servicio de base de datos no disponible"
        )
    
    logger.info(
        f"📊 Solicitando inventario completo: category={category or 'ALL'}"
    )
    
    result = supabase_service.products.get_products_hierarchical(
        category=category
    )
    
    if not result.get('success'):
        logger.error(f"❌ Error obteniendo inventario: {result.get('error')}")
        raise HTTPException(
            status_code=500,
            detail=result.get('error', 'Error al obtener inventario de productos')
        )
    
    return ProductHierarchyResponse(
        success=True,
        data=result.get('data', []),
        count=result.get('count', 0),
        page=1,
        pageSize=result.get('count', 0)
    )
