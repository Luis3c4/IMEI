from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import gspread
import requests
from google.oauth2.service_account import Credentials

app = Flask(__name__)
CORS(app)

IMEI_API_BASE = 'http://api-client.imei.org/api'
GOOGLE_SHEET_ID = os.environ.get('GOOGLE_SHEET_ID', '1e1P39zCbyfPD7jg_RbnEAzm_ZfOe7B5_VDVBQCZnjZM')
SHEET_NAME = 'Historial'
# Configuración de Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# ============================================
# FUNCIONES DE API GOOGLE SHEETS
# ============================================

def get_sheets_client():
    """Obtiene el cliente de Google Sheets"""
    try:
        # Opción 1: Usar archivo de credenciales JSON
        if os.path.exists('credentials.json'):
            creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=SCOPES
            )
        # Opción 2: Usar variable de entorno (para deployment en Render)
        elif os.environ.get('GOOGLE_CREDENTIALS_JSON'):
            import json
            creds_dict = json.loads(os.environ.get('GOOGLE_CREDENTIALS_JSON'))
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=SCOPES
            )
        else:
            raise Exception('No se encontraron credenciales de Google')
        
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Error al conectar con Google Sheets: {str(e)}")
        return None
    
def inicializar_sheet():
    """Crea el header del sheet si no existe"""
    try:
        client = get_sheets_client()
        if not client:
            return False
        
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)
        
        # Verificar si ya tiene headers
        first_row = sheet.row_values(1)
        
        if not first_row:
            # Crear headers
            headers = [
                'Fecha Consulta',
                'Input',
                'Serial Number',
                'Model',
                'IMEI',
                'IMEI2',
                'Warranty Status',
                'Purchase Date',
                'Simlock',
                'Carrier',
                'iCloud Status',
                'FMI Status',
                'Activated',
                'Blacklist'
            ]
            sheet.append_row(headers)
            
            # Formatear headers (bold)
            sheet.format('A1:N1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.2, 'green': 0.5, 'blue': 0.8}
            })
            
        return True
    except Exception as e:
        print(f"Error al inicializar sheet: {str(e)}")
        return False
    
def agregar_al_sheet(device_info, input_value):
    """Agrega una nueva fila al Google Sheet"""
    try:
        client = get_sheets_client()
        if not client:
            return False, "Error al conectar con Google Sheets"
        
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)
        
        # Preparar nueva fila
        nueva_fila = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            input_value,
            device_info.get('Serial Number', ''),
            device_info.get('Model', ''),
            device_info.get('IMEI', ''),
            device_info.get('IMEI 2', device_info.get('IMEI2', '')),
            device_info.get('Warranty Status', ''),
            device_info.get('Estimated Purchase Date', ''),
            device_info.get('Simlock', ''),
            device_info.get('Carrier', device_info.get('Initial Carrier', '')),
            device_info.get('iCloud', ''),
            device_info.get('FMI', ''),
            device_info.get('Activated', ''),
            device_info.get('Blacklist Status', ''),
        ]
        
        # Agregar fila al sheet
        sheet.append_row(nueva_fila)
        
        # Obtener número total de filas (menos el header)
        total_rows = len(sheet.get_all_values()) - 1
        
        return True, total_rows
    except Exception as e:
        print(f"Error al agregar al sheet: {str(e)}")
        return False, str(e)
    
def obtener_stats_sheet():
    """Obtiene estadísticas del Google Sheet"""
    try:
        client = get_sheets_client()
        if not client:
            return {
                'total_consultas': 0,
                'sheet_existe': False,
                'error': 'No se pudo conectar con Google Sheets'
            }
        
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)
        all_values = sheet.get_all_values()
        
        # Contar filas (menos header)
        total_consultas = len(all_values) - 1 if len(all_values) > 0 else 0
        
        # Última consulta
        ultima_consulta = None
        if len(all_values) > 1:
            ultima_fila = all_values[-1]
            ultima_consulta = ultima_fila[0] if len(ultima_fila) > 0 else None
        
        return {
            'total_consultas': total_consultas,
            'sheet_existe': True,
            'ultima_consulta': ultima_consulta,
            'sheet_url': f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}'
        }
    except Exception as e:
        return {
            'total_consultas': 0,
            'sheet_existe': False,
            'error': str(e)
        }
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
    if not data:
        return jsonify({'error': 'Body JSON requerido'}), 400
    api_key = data.get('api_key')
    service_id = data.get('service_id', '17')
    input_value = data.get('input_value')
    if not api_key or not service_id or not input_value:
        return jsonify({
            "success": False,
            "message": "api_key, service_id e input_value son obligatorios"
        }), 400
    result = consultar_dispositivo_api(api_key, service_id, input_value)
    if result['success']:
        sheet_success, total_o_error = agregar_al_sheet(result['data'], input_value)
        
        if sheet_success:
            result['sheet_updated'] = True
            result['total_registros'] = total_o_error
            result['sheet_url'] = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}'
        else:
            result['sheet_updated'] = False
            result['sheet_error'] = total_o_error
    return jsonify(result)

@app.route('/api/sheet-stats', methods=['GET'])
def sheet_stats():
    """Obtiene estadísticas del Google Sheet"""
    stats = obtener_stats_sheet()
    return jsonify(stats)

@app.route('/api/sheet-url', methods=['GET'])
def get_sheet_url():
    """Devuelve la URL del Google Sheet"""
    return jsonify({
        'url': f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}',
        'sheet_id': GOOGLE_SHEET_ID
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Backend Flask - Consultor IMEI con Google Sheets")
    print("="*70)
    print("📡 API REST: http://localhost:5000")
    print(f"🔗 IMEI.org API: {IMEI_API_BASE}")
    print(f"📊 Google Sheet ID: {GOOGLE_SHEET_ID}")
    print("="*70)
    print("\n📋 Inicializando Google Sheet...")
    
    if inicializar_sheet():
        print("✅ Google Sheet inicializado correctamente")
    else:
        print("⚠️  No se pudo inicializar Google Sheet (verifica credenciales)")
    
    print("\n📋 Endpoints disponibles:")
    print("   GET  /api/health          - Health check")
    print("   POST /api/balance         - Verificar balance")
    print("   POST /api/services        - Obtener servicios")
    print("   POST /api/consultar       - Consultar y guardar en Sheet")
    print("   GET  /api/sheet-stats     - Estadísticas del Sheet")
    print("   GET  /api/sheet-url       - URL del Google Sheet")
    print("="*70 + "\n")
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )
