"""
Ruta proxy para el servicio OCR de transferencias bancarias.
El frontend NO llama directamente al OCR service — pasa siempre por aquí,
donde se valida JWT de Supabase y se registra el log de auditoría.
"""
import logging
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.middleware import get_current_user_id
from app.services.supabase_service import supabase_service
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/ocr")
async def scan_transfer_image(
    image: UploadFile = File(..., description="Captura de la transferencia bancaria"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Proxy seguro hacia el microservicio OCR (IMEI-ocr).

    1. Valida JWT del usuario (Supabase).
    2. Reenvía la imagen al OCR service por red interna de Railway.
    3. Persiste log de auditoría en transfer_ocr_logs (sin guardar la imagen).
    4. Retorna los campos extraídos al frontend.

    Handler `async def` porque usa httpx asíncrono para el OCR service,
    con `run_in_executor` para la escritura síncrona en Supabase.
    """
    if not settings.OCR_SERVICE_URL:
        raise HTTPException(
            status_code=503,
            detail="Servicio OCR no configurado. Contacte al administrador.",
        )

    # Validar tipo de archivo
    content_type = image.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Tipo de archivo no soportado: '{content_type}'. Use PNG, JPEG o WEBP.",
        )

    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=422, detail="La imagen está vacía.")
    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen excede el límite de 10 MB.")

    # Reenviar al microservicio OCR
    ocr_url = settings.OCR_SERVICE_URL.rstrip("/") + "/ocr/extract"
    headers = {}
    if settings.OCR_API_KEY:
        headers["X-OCR-API-Key"] = settings.OCR_API_KEY

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                ocr_url,
                files={"image": (image.filename or "upload.png", image_bytes, content_type)},
                headers=headers,
            )
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="No se pudo conectar con el servicio OCR.")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="El servicio OCR tardó demasiado. Intente con una imagen más pequeña.")

    if response.status_code != 200:
        logger.error("OCR service respondió %s: %s", response.status_code, response.text)
        raise HTTPException(
            status_code=502,
            detail="El servicio OCR devolvió un error. Intente nuevamente.",
        )

    ocr_result = response.json()

    return ocr_result
