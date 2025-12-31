"""
RENIEC Routes - Endpoints para consulta de información de personas
Integra la API externa de RENIEC para consultar datos por DNI
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from app.schemas import ReniecDNIResponse, ErrorResponse
from app.services.reniec_service import ReniecService

logger = logging.getLogger(__name__)

router = APIRouter()
reniec_service = ReniecService()


@router.get(
    "/dni",
    response_model=ReniecDNIResponse,
    summary="Consultar información por DNI",
    responses={
        200: {"description": "Consulta exitosa"},
        400: {"model": ErrorResponse, "description": "DNI inválido o no encontrado"},
        401: {"model": ErrorResponse, "description": "Token de autorización inválido"},
        500: {"model": ErrorResponse, "description": "Error del servidor"}
    }
)
async def consultar_dni(
    numero: str = Query(
        ...,
        description="Número de DNI (8 dígitos)",
        min_length=8,
        max_length=8,
        regex="^[0-9]{8}$",
        examples=["46027897"]
    )
):
    """
    Consulta información de una persona usando su número de DNI
    
    **Parámetros:**
    - **numero** (str): Número de DNI de 8 dígitos (requerido)
    
    **Respuesta:**
    - first_name: str - Nombres de la persona
    - first_last_name: str - Apellido paterno
    - second_last_name: str - Apellido materno
    - full_name: str - Nombre completo
    - document_number: str - Número de DNI
    
    **Errores:**
    - 400: DNI inválido o no encontrado
    - 401: Token de autorización inválido
    - 500: Error del servidor o de conexión
    """
    try:
        logger.info(f"Iniciando consulta de DNI: {numero}")
        
        # Validar formato de DNI
        if not numero.isdigit():
            raise HTTPException(
                status_code=400,
                detail="El DNI debe contener solo números"
            )
        
        # Consultar en RENIEC
        result = await reniec_service.consultar_dni(numero)
        
        if not result['success']:
            status_code = result.get('status_code', 500)
            error_message = result.get('error', 'Error desconocido')
            
            logger.error(f"Error en consulta DNI {numero}: {error_message}")
            raise HTTPException(
                status_code=status_code,
                detail=error_message
            )
        
        # Retornar datos
        data = result['data']
        logger.info(f"Consulta exitosa para DNI: {numero}")
        
        return ReniecDNIResponse(
            first_name=data['first_name'],
            first_last_name=data['first_last_name'],
            second_last_name=data['second_last_name'],
            full_name=data['full_name'],
            document_number=data['document_number']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error inesperado en endpoint consultar_dni: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
