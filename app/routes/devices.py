"""
Device Routes - Endpoints para consulta de dispositivos
Maneja todas las peticiones relacionadas con consulta de IMEI
"""

import logging
from fastapi import APIRouter, HTTPException
from app.schemas import (
    QueryDeviceRequest, QueryDeviceResponse, ErrorResponse,
    BalanceResponse, ServicesResponse, HistoryRequest, HistoryResponse
)
from app.services.dhru_service import DHRUService
from app.services.sheets_service import SheetsService
from app.services.supabase_service import SupabaseService
from app.utils.validators import DeviceInputValidator
from app.utils.parsers import normalize_keys, parse_model_description

logger = logging.getLogger(__name__)

router = APIRouter()
dhru_service = DHRUService()
sheets_service = SheetsService()
supabase_service = SupabaseService()


@router.post(
    "/consultar",
    response_model=QueryDeviceResponse,
    summary="Consultar información de dispositivo",
    responses={
        200: {"description": "Consulta exitosa"},
        400: {"model": ErrorResponse, "description": "Error en validación"}
    }
)
async def query_device(request: QueryDeviceRequest):
    """
    Consulta información detallada de un dispositivo usando su IMEI
    
    **Parámetros:**
    - **input_value** (str): IMEI del dispositivo (requerido)
    - **service_id** (str): ID del servicio DHRU (default: 30)
    - **formato** (str): Formato de respuesta - beta, json, html (default: beta)
    
    **Respuesta:**
    - success: bool - Indica si la consulta fue exitosa
    - data: dict - Información del dispositivo
    - balance: float - Balance actual de la cuenta
    - price: float - Precio de la consulta
    - order_id: str - ID del pedido
    - sheet_updated: bool - Si se guardó en Google Sheets
    - supabase_saved: bool - Si se guardó en Supabase
    - parsed_model: dict - Información parseada del modelo (brand, color, capacity, etc)
    
    **Errores:**
    - 400: IMEI inválido o formato incorrecto
    """
    
    # 1. VALIDAR INPUT
    validation = DeviceInputValidator.validate(request.input_value)
    if not validation['valid']:
        raise HTTPException(
            status_code=400,
            detail=validation['message']
        )
    
    # 2. CONSULTAR DHRU
    try:
        result = dhru_service.query_device(
            service_id=request.service_id,
            imei=request.input_value,
            format=request.formato
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error consultando DHRU: {str(e)}"
        )
    
    # 3. GUARDAR EN GOOGLE SHEETS si fue exitoso
    if result['success']:
        result['data'] = normalize_keys(result['data'])
        
        try:
            sheets_result = sheets_service.add_record(
                device_info=result['data'],
                metadata={
                    'input_value': request.input_value,
                    'service_id': request.service_id,
                    'order_id': result.get('order_id'),
                    'price': result.get('price'),
                    'balance': result.get('balance')
                }
            )
            result['sheet_updated'] = sheets_result['success']
            if sheets_result['success']:
                result['total_registros'] = sheets_result.get('total_records', 0)
                result['sheet_url'] = f"https://docs.google.com/spreadsheets/d/{sheets_service.sheet_id}"
        except Exception as e:
            # Si falla Google Sheets, no bloqueamos la respuesta
            result['sheet_updated'] = False
            result['sheet_error'] = str(e)
        
        # 4. GUARDAR EN SUPABASE si está conectado
        try:
            # Parsear el Model_Description
            model_desc = result['data'].get('Model_Description', '')
            parsed_model = parse_model_description(model_desc)
            
            logger.info(f"📱 Modelo parseado: {parsed_model}")
            
            # Guardar en Supabase
            supabase_result = supabase_service.save_device_query(
                device_info=result['data'],
                metadata={
                    'input_value': request.input_value,
                    'service_id': request.service_id,
                    'order_id': result.get('order_id'),
                    'price': result.get('price'),
                    'balance': result.get('balance')
                },
                parsed_model=parsed_model
            )
            
            result['supabase_saved'] = supabase_result['success']
            if supabase_result['success']:
                result['supabase_ids'] = {
                    'product_id': supabase_result.get('product_id'),
                    'variant_id': supabase_result.get('variant_id'),
                    'item_id': supabase_result.get('item_id')
                }
                result['parsed_model'] = parsed_model
                logger.info(f"✅ Guardado en Supabase: {supabase_result}")
            else:
                result['supabase_error'] = supabase_result.get('error')
                logger.error(f"❌ Error guardando en Supabase: {supabase_result.get('error')}")
                
        except Exception as e:
            # Si falla Supabase, no bloqueamos la respuesta
            result['supabase_saved'] = False
            result['supabase_error'] = str(e)
            logger.error(f"❌ Excepción guardando en Supabase: {str(e)}")
    
    return result


@router.get(
    "/balance",
    response_model=BalanceResponse,
    summary="Obtener balance de cuenta"
)
async def get_balance():
    """
    Obtiene el balance disponible en la cuenta DHRU
    
    **Respuesta:**
    - success: bool - True si se obtuvo el balance
    - balance: float - Monto disponible en la cuenta
    - message: str - Mensaje descriptivo
    """
    try:
        result = dhru_service.get_balance()
        if result['success']:
            result['message'] = "Balance obtenido correctamente"
        else:
            result['message'] = result.get('error', 'Error obteniendo balance')
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo balance: {str(e)}"
        )


@router.get(
    "/services",
    response_model=ServicesResponse,
    summary="Obtener servicios disponibles"
)
async def get_services():
    """
    Obtiene la lista de servicios disponibles en DHRU
    
    **Respuesta:**
    - success: bool - True si se obtuvieron los servicios
    - services: list - Lista de servicios disponibles
    - total: int - Total de servicios
    - message: str - Mensaje descriptivo
    
    **Ejemplo de servicio:**
    ```json
    {
        "id": "30",
        "name": "iCloud Status",
        "price": "0.50"
    }
    ```
    """
    try:
        logger.info("Consultando servicios DHRU...")
        result = dhru_service.get_services()
        logger.info(f"Resultado de servicios: success={result.get('success')}")
        
        if result['success']:
            result['total'] = len(result.get('services', []))
            result['message'] = "Servicios obtenidos correctamente"
        else:
            # En caso de error, asegurar que los campos opcionales existan
            error_msg = result.get('error', 'Error obteniendo servicios')
            logger.error(f"Error obteniendo servicios: {error_msg}")
            result['services'] = []
            result['total'] = 0
            result['message'] = error_msg
        return result
    except Exception as e:
        logger.error(f"Excepción en get_services: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo servicios: {str(e)}"
        )

@router.post(
    "/historial",
    response_model=HistoryResponse,
    summary="Buscar en historial de órdenes"
)
async def search_history(request: HistoryRequest):
    """
    Busca en el historial de órdenes usando IMEI u Order ID
    
    **Parámetros:**
    - **imei_o_order_id** (str): IMEI u Order ID a buscar (requerido)
    - **formato** (str): Formato de respuesta - beta, json, html (default: beta)
    
    **Respuesta:**
    - success: bool - True si se encontraron registros
    - data: dict - Datos del historial encontrado
    - message: str - Mensaje descriptivo
    
    **Ejemplo de respuesta:**
    ```json
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
    ```
    """
    
    if not request.imei_o_order_id:
        raise HTTPException(
            status_code=400,
            detail="imei_o_order_id es requerido"
        )
    
    try:
        result = dhru_service.search_history(
            imei_or_order=request.imei_o_order_id,
            format=request.formato
        )
        
        # Normalizar keys si hay datos
        if result['success'] and result.get('data'):
            result['data'] = normalize_keys(result['data'])
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error buscando en historial: {str(e)}"
        )

