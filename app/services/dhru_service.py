from typing import Dict, Any
import requests
import logging
from ..config import settings
from app.utils.parsers import normalize_keys

# Configurar logging
logger = logging.getLogger(__name__)

class DHRUService:
    """Servicio para manejar todas las interacciones con DHRU API"""
    
    def __init__(self):
        self.base_url = settings.DHRU_API_BASE
        self.api_key = settings.DHRU_API_KEY
        self.timeout = 60
    
    def get_balance(self) -> Dict[str, Any]:
        """Obtiene balance de la cuenta"""
        try:
            response = requests.get(
                self.base_url,
                params={'action': 'balance', 'key': self.api_key},
                timeout=10
            )
            return {
                'success': True,
                'balance': float(response.text.strip())
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def query_device(self, service_id: str, imei: str, format: str = 'beta') -> Dict[str, Any]:
        """Consulta información de dispositivo"""
        try:
            response = requests.get(
                self.base_url,
                params={
                    'format': format,
                    'key': self.api_key,
                    'imei': imei,
                    'service': service_id
                },
                timeout=self.timeout
            )
            
            data = response.json()
            
            if data.get('status') == 'success':
                # Normalizar keys para frontend
                device_info = normalize_keys(data.get('result', {}))
                
                return {
                    'success': True,
                    'data': device_info,
                    'balance': data.get('balance'),
                    'price': data.get('price'),
                    'order_id': data.get('id')
                }
            
            return {
                'success': False,
                'error': data.get('result', 'Error desconocido')
            }
            
        except requests.Timeout:
            return {'success': False, 'error': 'Timeout de 60 segundos excedido'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    def get_services(self) -> Dict[str, Any]:
        """Obtiene lista de servicios disponibles"""
        try:
            logger.info(f"Consultando servicios DHRU: {self.base_url}")
            response = requests.get(
                self.base_url,
                params={'action': 'services', 'key': self.api_key},
                timeout=10
            )
            
            # Log del status code
            logger.info(f"Status code: {response.status_code}")
            
            # Intentar parsear JSON
            try:
                data = response.json()
                logger.info(f"Respuesta JSON recibida con {len(str(data))} caracteres")
            except ValueError as e:
                logger.error(f"Error parseando JSON. Respuesta raw: {response.text[:500]}")
                return {
                    'success': False,
                    'error': f'Respuesta no es JSON válido: {response.text[:100]}'
                }
            
            # DHRU devuelve la lista con la key "Service List"
            if 'Service List' in data:
                services = data['Service List']
                logger.info(f"Servicios obtenidos correctamente: {len(services)} servicios")
                return {
                    'success': True,
                    'services': services
                }
            
            # Si tiene formato estándar con status
            if data.get('status') == 'success':
                return {
                    'success': True,
                    'services': data.get('services', [])
                }
            
            # Log del error específico
            error_msg = data.get('result', data.get('message', 'Error desconocido'))
            logger.error(f"Error de API DHRU: {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
        except requests.Timeout:
            logger.error("Timeout al consultar servicios DHRU")
            return {'success': False, 'error': 'Timeout de 10 segundos excedido'}
        except requests.RequestException as e:
            logger.error(f"Error de conexión con DHRU: {str(e)}")
            return {'success': False, 'error': f'Error de conexión: {str(e)}'}
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            return {'success': False, 'error': f'Error inesperado: {str(e)}'}

    def search_history(self, imei_or_order: str, format: str = 'beta') -> Dict[str, Any]:
        """Busca en el historial de consultas"""
        try:
            response = requests.get(
                self.base_url,
                params={
                    'format': format,
                    'action': 'history',
                    'key': self.api_key,
                    'imei': imei_or_order
                },
                timeout=30
            )
            data = response.json()
            if format == 'beta' or format == 'json':
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
            return {'success': False, 'error': str(e)}


