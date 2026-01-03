"""
Rutas para manejar productos desde Supabase
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any , Optional
from pydantic import BaseModel
from app.services.supabase_service import supabase_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class Product(BaseModel):
    """Modelo de producto"""
    id: str
    name: str
    product_number: str
    serial_number: str
    item_price: str
    quantity: int
    category: str
    created_at: str
    updated_at: str


class ProductsResponse(BaseModel):
    """Respuesta de productos"""
    success: bool
    data: List[Dict[str, Any]]
    count: int
    error: Optional[str] = None


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
    
    result = supabase_service.get_products_with_variants()
    
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
