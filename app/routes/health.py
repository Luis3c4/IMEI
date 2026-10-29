"""
Health Check Endpoints
Verificar que el servidor esté funcionando correctamente
"""

from fastapi import APIRouter
from datetime import datetime
from app.config import settings
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health Check")
def health_check():
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


@router.get("/status", summary="Estado de la API e integraciones")
def status():
    """Informa el estado de la API y la configuración de sus destinos de datos."""
    return {
        "status": "ok",
        "integrations": {
            "supabase": {
                "role": "primary",
                "configured": bool(settings.SUPABASE_URL and settings.SUPABASE_KEY),
            },
            "google_sheets": {
                "role": "secondary",
                "configured": bool(settings.GOOGLE_CREDS_JSON and settings.SHEET_ID),
            },
        },
    }
