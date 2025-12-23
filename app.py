from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import gspread
import requests
from google.oauth2.service_account import Credentials
import re

app = Flask(__name__)
CORS(app)

DHRU_API_BASE = 'https://sickw.com/api.php'
DHRU_API_KEY = '1PA-6X8-BMQ-T28-X6H-8WP-7CL-GTK'
DHRU_API_USER = 'javie.apaza@gmail.com'

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
        first_row = sheet.row_values(1)
        
        if not first_row:
            headers = [
                'Fecha Consulta',
                'Input Consultado',
                'Serial Number',
                'Model Description',
                'IMEI',
                'IMEI2',
                'MEID',
                'Warranty Status',
                'Purchase Date',
                'Purchase Country',
                'Sim-Lock Status',
                'Locked Carrier',
                'iCloud Lock',
                'Demo Unit',
                'Loaner Device',
                'Refurbished Device',
                'Replaced Device',
                'Replacement Device',
                'Service ID',
                'Order ID',
                'Precio',
                'Balance Restante'
            ]
            sheet.append_row(headers)
            
            # Formatear headers (bold y color)
            sheet.format('A1:U1', {
                'textFormat': {'bold': True, 'fontSize': 11},
                'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.9},
                'horizontalAlignment': 'CENTER'
            })
            
            # Ajustar ancho de columnas
            sheet.format('A1:U1', {'wrapStrategy': 'WRAP'})
            
        return True
    except Exception as e:
        print(f"Error al inicializar sheet: {str(e)}")
        return False
    
def agregar_al_sheet(device_info, input_value, service_id, order_id='', precio='', balance=''):
    """Agrega una nueva fila al Google Sheet con todos los datos de DHRU"""
    try:
        client = get_sheets_client()
        if not client:
            return False, "Error al conectar con Google Sheets"
        
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(SHEET_NAME)
        
        # Construir fila con todos los campos de DHRU Fusion
        nueva_fila = [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),           # Fecha Consulta
            input_value,                                             # Input Consultado
            device_info.get('Serial Number', ''),                    # Serial Number
            device_info.get('Model Description', ''),                # Model Description
            device_info.get('IMEI', ''),                             # IMEI
            device_info.get('IMEI2', ''),                            # IMEI2
            device_info.get('MEID', ''),                             # MEID
            device_info.get('Warranty Status', ''),                  # Warranty Status
            device_info.get('Estimated Purchase Date', ''),          # Purchase Date
            device_info.get('Purchase Country', ''),                 # Purchase Country
            device_info.get('Sim-Lock Status', ''),                  # Sim-Lock Status
            device_info.get('Locked Carrier', ''),                   # Locked Carrier
            device_info.get('iCloud Lock', ''),                      # iCloud Lock
            device_info.get('Demo Unit', ''),                        # Demo Unit
            device_info.get('Loaner Device', ''),                    # Loaner Device
            device_info.get('Refurbished Device', ''),               # Refurbished Device
            device_info.get('Replaced Device', ''),                  # Replaced Device
            device_info.get('Replacement Device', ''),               # Replacement Device
            service_id,                                              # Service ID
            order_id,                                                # Order ID
            precio,                                                  # Precio
            balance                                                  # Balance Restante
        ]
        
        sheet.append_row(nueva_fila)
        
        # Aplicar formato a la fila recién agregada
        ultima_fila = len(sheet.get_all_values())
        
        # Formato condicional para iCloud Lock
        icloud_value = device_info.get('iCloud Lock', '')
        if icloud_value == 'ON':
            sheet.format(f'M{ultima_fila}', {
                'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.8},
                'textFormat': {'bold': True}
            })
        elif icloud_value == 'OFF':
            sheet.format(f'M{ultima_fila}', {
                'backgroundColor': {'red': 0.8, 'green': 1.0, 'blue': 0.8},
                'textFormat': {'bold': True}
            })
        
        # Formato condicional para Sim-Lock Status
        simlock_value = device_info.get('Sim-Lock Status', '')
        if simlock_value == 'Unlocked':
            sheet.format(f'K{ultima_fila}', {
                'backgroundColor': {'red': 0.8, 'green': 1.0, 'blue': 0.8}
            })
        elif simlock_value == 'Locked':
            sheet.format(f'K{ultima_fila}', {
                'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.8}
            })
        
        total_rows = ultima_fila - 1  # Restar el header
        
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
# FUNCIONES DE API SICKW
# ============================================
def verificar_balance_dhru():
    """Verifica el balance disponible en la cuenta DHRU"""
    try:
        url = f"{DHRU_API_BASE}"
        params = {
            'action': 'balance',
            'key': DHRU_API_KEY
        }
        
        print(f"\n Verificando balance en DHRU...")
        response = requests.get(url, params=params, timeout=10)
        
        # La respuesta es solo el número del balance
        balance = float(response.text.strip())
        
        return {
            'success': True,
            'balance': balance,
            'message': 'Balance obtenido correctamente'
        }
    except Exception as e:
        print(f"Error al obtener balance: {str(e)}")
        return {
            'success': False,
            'balance': 0,
            'message': f'Error de conexión: {str(e)}'
        }

def obtener_servicios_dhru():
    """Obtiene la lista de servicios disponibles en DHRU"""
    try:
        url = f"{DHRU_API_BASE}"
        params = {
            'action': 'services',
            'key': DHRU_API_KEY
        }
        
        print(f"\n Obteniendo servicios de DHRU...")
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'Service List' in data:
            services = data['Service List']
            return {
                'success': True,
                'services': services,
                'total': len(services),
                'message': 'Servicios obtenidos correctamente'
            }
        else:
            return {
                'success': False,
                'services': [],
                'message': 'No se encontraron servicios'
            }
    except Exception as e:
        print(f" Error al obtener servicios: {str(e)}")
        return {
            'success': False,
            'services': [],
            'message': f'Error de conexión: {str(e)}'
        }
    
def parsear_resultado_dhru(texto, formato='json'):
    """Parsea el resultado de DHRU y lo convierte a diccionario"""
    resultado = {}
    
    if formato == 'html':
        # Formato HTML: líneas separadas con saltos de línea
        lineas = texto.strip().split('\n')
        for linea in lineas:
            if ':' in linea:
                key, value = linea.split(':', 1)
                resultado[key.strip()] = value.strip()
    
    return resultado


def normalize_keys(obj):
    """Recursively replace whitespace in dict keys with underscores.

    Examples:
    - 'Serial Number' -> 'Serial_Number'
    - preserves nested dicts and lists
    """
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            # Only operate on string keys
            if isinstance(k, str):
                new_key = re.sub(r"\s+", "_", k.strip())
            else:
                new_key = k
            new[new_key] = normalize_keys(v)
        return new
    elif isinstance(obj, list):
        return [normalize_keys(i) for i in obj]
    else:
        return obj

def consultar_dispositivo_dhru(service_id, imei, formato='beta'):
    """
    Consulta información de un dispositivo en DHRU Fusion
    
    Parámetros:
    - service_id: ID del servicio a utilizar
    - imei: IMEI o Serial Number del dispositivo
    - formato: 'beta' (JSON completo), 'json' (JSON parcial), 'html' (texto simple)
    """
    try:
        url = f"{DHRU_API_BASE}"
        params = {
            'format': formato,
            'key': DHRU_API_KEY,
            'imei': imei,
            'service': service_id
        }
        
        print(f"\n DEBUG - Consultando dispositivo en DHRU:")
        print(f"   URL: {url}")
        print(f"   Service ID: {service_id}")
        print(f"   IMEI: {imei}")
        print(f"   Formato: {formato}")
        
        response = requests.get(url, params=params, timeout=60)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response (primeros 500 chars): {response.text[:500]}")
        
        # Parsear respuesta según formato
        if formato == 'beta' or formato == 'json':
            data = response.json()
            
            if data.get('status') == 'success':
                # Extraer información del resultado
                device_info = {}
                
                if formato == 'beta' and 'result' in data:
                    # Formato BETA tiene el resultado en objeto JSON
                    device_info = data['result']
                elif formato == 'json' and 'result' in data:
                    # Formato JSON tiene el resultado como string HTML
                    device_info = parsear_resultado_dhru(data['result'], 'html')
                
                return {
                    'success': True,
                    'data': device_info,
                    'raw_response': data,
                    'balance_restante': data.get('balance', 'N/A'),
                    'precio': data.get('price', 'N/A'),
                    'order_id': data.get('id', 'N/A'),
                    'message': 'Consulta exitosa'
                }
            elif data.get('status') == 'error':
                return {
                    'success': False,
                    'data': None,
                    'message': data.get('result', 'Error desconocido'),
                    'raw_response': data
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': 'Respuesta inesperada de la API',
                    'raw_response': data
                }
        
        elif formato == 'html':
            # Formato HTML devuelve texto plano
            device_info = parsear_resultado_dhru(response.text, 'html')
            
            if device_info:
                return {
                    'success': True,
                    'data': device_info,
                    'raw_response': response.text,
                    'message': 'Consulta exitosa'
                }
            else:
                return {
                    'success': False,
                    'data': None,
                    'message': 'No se pudo parsear la respuesta',
                    'raw_response': response.text
                }
        
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'data': None,
            'message': 'Timeout: La consulta tardó más de 60 segundos'
        }
    except requests.exceptions.JSONDecodeError:
        return {
            'success': False,
            'data': None,
            'message': f'La API no devolvió JSON válido. Respuesta: {response.text[:200]}',
            'error_type': 'JSONDecodeError'
        }
    except Exception as e:
        print(f" ERROR: {str(e)}")
        return {
            'success': False,
            'data': None,
            'message': f'Error de conexión: {str(e)}',
            'error_type': type(e).__name__
        }

def buscar_historial_dhru(imei_o_order_id, formato='beta'):
    """Busca en el historial de órdenes por IMEI o Order ID"""
    try:
        url = f"{DHRU_API_BASE}"
        params = {
            'format': formato,
            'key': DHRU_API_KEY,
            'imei': imei_o_order_id,
            'action': 'history'
        }
        
        print(f"\n Buscando en historial: {imei_o_order_id}")
        response = requests.get(url, params=params, timeout=30)
        
        if formato == 'beta' or formato == 'json':
            data = response.json()
            return {
                'success': True,
                'data': data,
                'message': 'Historial obtenido'
            }
        else:
            return {
                'success': True,
                'data': response.text,
                'message': 'Historial obtenido'
            }
    except Exception as e:
        return {
            'success': False,
            'data': None,
            'message': f'Error: {str(e)}'
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
        'api_provider': 'DHRU Fusion (sickw.com)',
        'timestamp': datetime.now().isoformat()
    })
@app.route('/api/balance', methods=['POST'])
def check_balance():
    """Endpoint para verificar balance"""
    result = verificar_balance_dhru()
    return jsonify(result)
@app.route('/api/services', methods=['POST'])
def get_services():
    """Endpoint para obtener servicios disponibles"""
    result = obtener_servicios_dhru()
    return jsonify(result)

@app.route('/api/consultar', methods=['POST'])
def consultar_dispositivo():
    data = request.json
    
    if not data:
        return jsonify({'error': 'Body JSON requerido'}), 400
    
    service_id = data.get('service_id', '30')  # Default: iCLOUD ON/OFF
    input_value = data.get('input_value')
    formato = data.get('formato', 'beta')  # beta, json o html
    
    if not input_value:
        return jsonify({
            'success': False,
            'message': 'input_value es obligatorio (IMEI o Serial)'
        }), 400
    
    # Consultar en DHRU
    result = consultar_dispositivo_dhru(service_id, input_value, formato)
    
    # Si fue exitoso, guardar en Google Sheet
    if result['success'] and result['data']:
        # Preserve the original data for internal use (Google Sheet),
        # but return a normalized version to the frontend (no spaces in keys).
        raw_device_info = result['data']
        sheet_success, total_o_error = agregar_al_sheet(
            device_info=raw_device_info,
            input_value=input_value,
            service_id=service_id,
            order_id=result.get('order_id', ''),
            precio=result.get('precio', ''),
            balance=result.get('balance_restante', '')
        )
        # Normalize keys for the response sent to the frontend
        try:
            normalized = normalize_keys(raw_device_info)
            result['data'] = normalized
        except Exception:
            # If normalization fails for any reason, leave original data
            pass
        if sheet_success:
            result['sheet_updated'] = True
            result['total_registros'] = total_o_error
            result['sheet_url'] = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}'
        else:
            result['sheet_updated'] = False
            result['sheet_error'] = total_o_error
    
    return jsonify(result)

@app.route('/api/historial', methods=['POST'])
def buscar_historial():
    """Endpoint para buscar en historial de órdenes"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'Body JSON requerido'}), 400
    
    imei_o_order = data.get('imei_o_order_id')
    formato = data.get('formato', 'beta')
    
    if not imei_o_order:
        return jsonify({
            'success': False,
            'message': 'imei_o_order_id es obligatorio'
        }), 400
    
    result = buscar_historial_dhru(imei_o_order, formato)
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
    print("Backend Flask - Consultor IMEI con Google Sheets")
    print("="*70)
    print(" API REST: http://localhost:5000")
    print(f" DHRU API: {DHRU_API_BASE}")
    print(f" Google Sheet ID: {GOOGLE_SHEET_ID}")
    print("="*70)
    print("\n Inicializando Google Sheet...")
    
    if inicializar_sheet():
        print(" Google Sheet inicializado correctamente")
    else:
        print("  No se pudo inicializar Google Sheet (verifica credenciales)")
    
    print("\n Endpoints disponibles:")
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
