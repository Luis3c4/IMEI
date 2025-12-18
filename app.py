from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import requests
app = Flask(__name__)
CORS(app)

IMEI_API_BASE = 'http://api-client.imei.org/api'

# ============================================
# FUNCIONES DE API IMEI.ORG
# ============================================

def verificar_balance_api(api_key):
    try:
        url = f"{IMEI_API_BASE}/balance"
        params = {'apikey': api_key}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get('status') == 1:
            return {
                'success': True,
                'balance': data['response']['credits'],
                'message': 'Balance obtenido correctamente'
            }
        else:
            return {
                'success': False,
                'balance': 0,
                'message': data.get('message', 'Error al obtener balance')
            }
    except Exception as e:
        return {
            'success': False,
            'balance': 0,
            'message': f'Error de conexión: {str(e)}'
        }
def obtener_servicios_api(api_key):
    try:
        url = f"{IMEI_API_BASE}/services"
        params = {'apikey': api_key}
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if data.get('status') == 1:
            return {
                'success': True,
                'services': data['response']['services'],
                'message': 'Servicios obtenidos correctamente'
            }
        else:
            return {
                'success': False,
                'services': [],
                'message': data.get('message', 'Error al obtener servicios')
            }
    except Exception as e:
        return {
            'success': False,
            'services': [],
            'message': f'Error de conexión: {str(e)}'
        }
def consultar_dispositivo_api(api_key, service_id, input_value):
    """Consulta información de un dispositivo por IMEI o Serial"""
    try:
        url = f"{IMEI_API_BASE}/submit"
        params = {
            'apikey': api_key,
            'service_id': service_id,
            'input': input_value
        }
        print("\n🔍 DEBUG - Consultando dispositivo:")
        print(f"   URL: {url}")
        print(f"   Service ID: {service_id}")
        print(f"   Input: {input_value}")
        print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
        response = requests.get(url, params=params, timeout=60)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Text (primeros 300 chars): {response.text[:300]}")
        
        data = response.json()
        if data.get("status") != 1:
            return {
                "success": False,
                "message": data.get("message", "Error en la consulta"),
                "data": None,
                "debug_response": data
            }
        
        if data.get('status') == 1 and 'response' in data:
            device_info = data['response']['services'][0]
            return {
                'success': True,
                'data': device_info,
                'message': 'Consulta exitosa'
                }
        else:
            return {
                'success': False,
                'data': None,
                'message': data.get('message', 'No se encontró información del dispositivo')
                }
    except requests.exceptions.JSONDecodeError:
        print("❌ ERROR: La respuesta no es JSON válido")
        print(f"   Response Text completo: {response.text}")
        return {
            'success': False,
            'data': None,
            'message': f'La API no devolvió JSON válido. Respuesta: {response.text[:200]}',
            'error_type': 'JSONDecodeError',
            'status_code': response.status_code
        }
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'data': None,
            'message': 'Timeout: La consulta tardó más de 60 segundos'
        }
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error de conexión: {str(e)}',
            'error_type': type(e).__name__
        }

# ============================================
# endpoints de la API
# ============================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica que el servidor esté funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Servidor funcionando correctamente',
        'timestamp': datetime.now().isoformat()
    })
@app.route('/api/balance', methods=['POST'])
def check_balance():
    """Endpoint para verificar balance"""
    data = request.json
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key requerida'}), 400
    
    result = verificar_balance_api(api_key)
    return jsonify(result)
@app.route('/api/services', methods=['POST'])
def get_services():
    """Endpoint para obtener servicios disponibles"""
    data = request.json
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key requerida'}), 400
    
    result = obtener_servicios_api(api_key)
    return jsonify(result)
@app.route('/api/consultar', methods=['POST'])
def consultar_dispositivo():
    data = request.json
    api_key = data.get('api_key')
    service_id = data.get('service_id', '171')
    input_value = data.get('input_value')
    if not api_key or not service_id or not input_value:
        return jsonify({
            "success": False,
            "message": "api_key, service_id e input_value son obligatorios"
        }), 400
    result = consultar_dispositivo_api(api_key, service_id, input_value)
    return jsonify(result)

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
