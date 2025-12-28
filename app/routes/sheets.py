"""
Google Sheets Routes
Endpoints para gestionar el historial en Google Sheets
"""

from fastapi import APIRouter, HTTPException
from app.schemas import StatsResponse, SheetUrlResponse
from app.services.sheets_service import SheetsService

router = APIRouter()
sheets_service = SheetsService()


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Obtener estadísticas del Sheet"
)
async def get_stats():
    """
    Obtiene estadísticas del Google Sheet con historial de consultas
    
    **Respuesta:**
    - success: bool - True si se obtuvieron las estadísticas
    - total_consultas: int - Total de consultas registradas
    - ultima_consulta: str - Timestamp de la última consulta
    - sheet_url: str - URL del Google Sheet
    - sheet_existe: bool - Si el sheet existe
    
    **Ejemplo de respuesta:**
    ```json
    {
        "success": true,
        "total_consultas": 150,
        "ultima_consulta": "2024-01-15 14:30:00",
        "sheet_url": "https://docs.google.com/spreadsheets/d/...",
        "sheet_existe": true
    }
    ```
    """
    try:
        stats = sheets_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@router.get(
    "/url",
    response_model=SheetUrlResponse,
    summary="Obtener URL del Google Sheet"
)
async def get_url():
    """
    Devuelve la URL e ID del Google Sheet
    
    **Respuesta:**
    - url: str - URL accesible del Google Sheet
    - sheet_id: str - ID único del sheet
    - error: str - Si ocurre un error
    
    **Ejemplo de respuesta:**
    ```json
    {
        "url": "https://docs.google.com/spreadsheets/d/1e1P39zCbyfPD7jg_RbnEAzm_ZfOe7B5_VDVBQCZnjZM/edit",
        "sheet_id": "1e1P39zCbyfPD7jg_RbnEAzm_ZfOe7B5_VDVBQCZnjZM"
    }
    ```
    """
    try:
        url_info = sheets_service.get_sheet_url()
        return url_info
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo URL del sheet: {str(e)}"
        )

