from typing import Dict, Any
import requests
from ..config import settings
from app.utils.parsers import normalize_keys

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
            response = requests.get(
                self.base_url,
                params={'action': 'services', 'key': self.api_key},
                timeout=10
            )
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'success': True,
                    'services': data.get('services', [])
                }
            return {
                'success': False,
                'error': data.get('result', 'Error desconocido')
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

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


