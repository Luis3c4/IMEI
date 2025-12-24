from flask import Blueprint, request, jsonify
from ..services.dhru_service import DHRUService
from ..services.sheets_service import SheetsService
from app.utils.validators import DeviceInputValidator
from ..utils.parsers import normalize_keys

devices_bp = Blueprint('devices', __name__)
dhru_service = DHRUService()
sheets = SheetsService()

@devices_bp.route('/consultar', methods=['POST'])
def query_device():

    data = request.json
    if not data or not data.get('input_value'):
        return jsonify({'error': 'input_value requerido'}), 400
    
     # 1. VALIDAR INPUT
    validation = DeviceInputValidator.validate(data.get('input_value'))
    if not validation['valid']:
        return jsonify({
            'success': False,
            'message': validation['message']
        }), 400    
    
    # Consultar DHRU
    result = dhru_service.query_device(
        service_id=data.get('service_id', '30'),
        imei=data['input_value'],
        format=data.get('formato', 'beta')
    )
    
    # Guardar en Sheets si exitoso
    if result['success']:
        result['data'] = normalize_keys(result['data'])
        sheets_result = sheets.add_record(
            device_info=result['data'],
            metadata={
                'input_value': data['input_value'],
                'service_id': data.get('service_id', '30'),
                'order_id': result.get('order_id'),
                'price': result.get('price'),
                'balance': result.get('balance')
            }
        )
        result['sheet_updated'] = sheets_result['success']
        if sheets_result['success']:
            result['total_registros'] = sheets_result.get('total_records', 0)
            result['sheet_url'] = sheets_result.get('sheet_url')
        else:
            result['sheet_error'] = sheets_result.get('error')
    
    return jsonify(result)

@devices_bp.route('/balance', methods=['POST', 'GET'])
def check_balance():
    """
    Verifica el balance disponible en la cuenta DHRU
    
    Métodos: POST, GET
    
    Respuesta:
    {
        "success": true,
        "balance": 150.50,
        "message": "Balance obtenido correctamente"
    }
    """
    result = dhru_service.get_balance()
    return jsonify(result)
@devices_bp.route('/services', methods=['POST', 'GET'])
def get_services():
    """
    Obtiene la lista de servicios disponibles en DHRU
    
    Métodos: POST, GET
    
    Respuesta:
    {
        "success": true,
        "services": [
            {"id": "30", "name": "iCloud Status", "price": "0.50"},
            ...
        ],
        "total": 50,
        "message": "Servicios obtenidos correctamente"
    }
    """
    result = dhru_service.get_services()
    return jsonify(result)

@devices_bp.route('/historial', methods=['POST'])
def search_history():
    """
    Busca en el historial de órdenes por IMEI o Order ID
    
    Body JSON:
    {
        "imei_o_order_id": "356789012345678",  // IMEI o Order ID
        "formato": "beta"                       // Opcional: beta, json, html
    }
    
    Respuesta:
    {
        "success": true,
        "data": {
            "orders": [
                {
                    "id": "12345",
                    "imei": "356789012345678",
                    "service": "iCloud Status",
                    "price": "0.50",
                    "date": "2024-01-15 10:30:00",
                    "status": "completed"
                }
            ]
        },
        "message": "Historial obtenido"
    }
    """
    data = request.json
    
    # Validación
    if not data or not data.get('imei_o_order_id'):
        return jsonify({
            'success': False,
            'error': 'imei_o_order_id es requerido'
        }), 400
    
    # Buscar en historial
    result = dhru_service.search_history(
        imei_or_order=data.get('imei_o_order_id'),
        format=data.get('formato', 'beta')
    )
    
    # Normalizar keys si hay datos
    if result['success'] and result.get('data'):
        result['data'] = normalize_keys(result['data'])
    
    return jsonify(result)
