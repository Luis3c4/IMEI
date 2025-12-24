from flask import Blueprint, jsonify
from ..services.sheets_service import SheetsService

sheets_bp = Blueprint('sheets', __name__)
sheets_service = SheetsService()


@sheets_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Obtiene estadísticas del Google Sheet
    
    Respuesta:
    {
        "success": true,
        "total_consultas": 150,
        "ultima_consulta": "2024-01-15 14:30:00",
        "sheet_url": "https://docs.google.com/spreadsheets/d/...",
        "sheet_existe": true
    }
    """
    stats = sheets_service.get_stats()
    return jsonify(stats)


@sheets_bp.route('/url', methods=['GET'])
def get_url():
    """
    Devuelve la URL del Google Sheet
    
    Respuesta:
    {
        "url": "https://docs.google.com/spreadsheets/d/...",
        "sheet_id": "1e1P39zCbyfPD7jg_..."
    }
    """
    url_info = sheets_service.get_sheet_url()
    return jsonify(url_info)
