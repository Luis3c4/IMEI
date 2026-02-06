"""
Servicio para interactuar con la API de RENIEC
Permite consultar información de personas por DNI
Implementa cache local en BD para reducir llamadas externas
"""

from typing import Dict, Any
import httpx
import logging
from app.config import settings
from app.services.supabase_service import supabase_service

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
        Consulta información de una persona por DNI.
        Primero verifica en la base de datos local.
        Si no existe, consulta la API externa.
        
        Args:
            numero: Número de DNI (8 dígitos)
        
        Returns:
            Dict con la información de la persona o error
        """
        try:
            # 1. Intentar obtener datos de la BD primero
            logger.info(f"🔍 Verificando DNI {numero} en base de datos local...")
            db_result = supabase_service.customers.get_customer_reniec_data(numero)
            
            if db_result['success']:
                logger.info(f"✅ Datos encontrados en BD para DNI: {numero}")
                return {
                    'success': True,
                    'data': db_result['data'],
                    'source': 'database'  # Indicador de que vino de BD
                }
            
            # 2. Si no hay datos en BD, consultar API externa
            logger.info(f"🌐 Consultando API externa de RENIEC para DNI: {numero}")
            
            # Validar que el token esté configurado
            if not self.api_token:
                logger.error("RENIEC_API_TOKEN no está configurado")
                return {
                    'success': False,
                    'error': 'Token de API no configurado. Configure RENIEC_API_TOKEN en las variables de entorno.'
                }
            
            # Construir URL
            url = f"{self.base_url}/dni"
            
            # Realizar petición a API externa
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params={'numero': numero},
                    headers=self._get_headers()
                )
                
                # Verificar código de estado
                if response.status_code == 200:
                    data = response.json()
                    
                    # Convertir nombres a formato título (Primera Letra Mayúscula)
                    if 'first_name' in data and data['first_name']:
                        data['first_name'] = data['first_name'].title()
                    if 'first_last_name' in data and data['first_last_name']:
                        data['first_last_name'] = data['first_last_name'].title()
                    if 'second_last_name' in data and data['second_last_name']:
                        data['second_last_name'] = data['second_last_name'].title()
                    if 'full_name' in data and data['full_name']:
                        data['full_name'] = data['full_name'].title()
                    
                    # 3. Guardar datos en BD para futuras consultas
                    logger.info(f"💾 Guardando datos de RENIEC en BD para DNI: {numero}")
                    save_result = supabase_service.customers.update_customer_reniec_data(
                        numero, data
                    )
                    
                    if not save_result['success']:
                        logger.warning(f"⚠️ No se pudo guardar datos de RENIEC en BD: {save_result.get('error')}")
                    
                    logger.info(f"✅ Consulta exitosa para DNI: {numero}")
                    return {
                        'success': True,
                        'data': data,
                        'source': 'api'  # Indicador de que vino de API externa
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
