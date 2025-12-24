"""
Endpoints de health check y sistema
"""
from flask import Blueprint, jsonify
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Verifica que el servidor esté funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Servidor funcionando correctamente',
        'api_provider': 'DHRU Fusion (sickw.com)',
        'timestamp': datetime.now().isoformat()
    })