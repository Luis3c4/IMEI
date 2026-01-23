"""
Servicio para interactuar con la API de RENIEC
Permite consultar información de personas por DNI
"""

from typing import Dict, Any
import httpx
import logging
from app.config import settings

# Configurar logging
logger = logging.getLogger(__name__)


class ReniecService:
    """Servicio para manejar las interacciones con RENIEC API"""
    
    def __init__(self):
        self.base_url = settings.RENIEC_API_BASE
        self.api_token = settings.RENIEC_API_TOKEN
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        """Construye los headers necesarios para la API"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
    
    async def consultar_dni(self, numero: str) -> Dict[str, Any]:
        """
        Consulta información de una persona por DNI
        
        Args:
            numero: Número de DNI (8 dígitos)
            
        Returns:
            Dict con la información de la persona o error
        """
        try:
            # Validar que el token esté configurado
            if not self.api_token:
                logger.error("RENIEC_API_TOKEN no está configurado")
                return {
                    'success': False,
                    'error': 'Token de API no configurado. Configure RENIEC_API_TOKEN en las variables de entorno.'
                }
            
            # Construir URL
            url = f"{self.base_url}/dni"
            
            # Realizar petición
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Consultando DNI: {numero}")
                response = await client.get(
                    url,
                    params={'numero': numero},
                    headers=self._get_headers()
                )
                
                # Verificar código de estado
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Consulta exitosa para DNI: {numero}")
                    return {
                        'success': True,
                        'data': data
                    }
                elif response.status_code == 400:
                    logger.warning(f"DNI inválido o no encontrado: {numero}")
                    return {
                        'success': False,
                        'error': 'DNI inválido o no encontrado',
                        'status_code': 400
                    }
                elif response.status_code == 401:
                    logger.error("Token de autorización inválido")
                    return {
                        'success': False,
                        'error': 'Token de autorización inválido',
                        'status_code': 401
                    }
                else:
                    logger.error(f"Error en API RENIEC: {response.status_code}")
                    return {
                        'success': False,
                        'error': f'Error en la API: {response.status_code}',
                        'status_code': response.status_code
                    }
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout al consultar DNI: {numero}")
            return {
                'success': False,
                'error': 'Timeout al consultar la API de RENIEC'
            }
        except httpx.RequestError as e:
            logger.error(f"Error de conexión con RENIEC: {str(e)}")
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error inesperado al consultar DNI: {str(e)}")
            return {
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }
