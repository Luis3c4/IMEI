"""
Health Check Endpoints
Verificar que el servidor esté funcionando correctamente
"""

from fastapi import APIRouter
from datetime import datetime
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health Check")
async def health_check():
    """
    Verifica que el servidor esté funcionando correctamente
    
    Returns:
        HealthResponse: Estado del servidor con timestamp
    """
    return {
        "status": "ok",
        "message": "Servidor funcionando correctamente",
        "api_provider": "DHRU Fusion (sickw.com)",
        "timestamp": datetime.now().isoformat()
    }
