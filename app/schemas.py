"""
Pydantic models para validación de datos de entrada y salida
Estos modelos proporcionan validación automática y documentación en Swagger
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict, List


# ============ DEVICE ENDPOINTS ============

class QueryDeviceRequest(BaseModel):
    """Solicitud para consultar información de dispositivo"""
    input_value: str = Field(
        ...,
        description="IMEI del dispositivo",
        json_schema_extra={"example": "356789012345678"}
    )
    product_number: Optional[str] = Field(
        default=None,
        description="Product Number ingresado manualmente (opcional)",
        json_schema_extra={"example": "MXN93LL/A"}
    )
    service_id: str = Field(
        default="30",
        description="ID del servicio DHRU",
        json_schema_extra={"example": "30"}
    )
    formato: str = Field(
        default="beta",
        description="Formato de respuesta",
        json_schema_extra={"example": "beta"}
    )
    
    # Pydantic v2: usar model_config para ejemplos del cuerpo
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "input_value": "356789012345678",
                    "product_number": "MXN93LL/A",
                    "service_id": "30",
                    "formato": "beta"
                }
            ]
        }
    )


class DeviceInfo(BaseModel):
    """Información de un dispositivo"""
    serial_number: Optional[str] = None
    model_description: Optional[str] = None
    imei: Optional[str] = None
    imei2: Optional[str] = None
    meid: Optional[str] = None
    warranty_status: Optional[str] = None
    purchase_country: Optional[str] = None
    sim_lock_status: Optional[str] = None
    locked_carrier: Optional[str] = None
    icloud_lock: Optional[str] = None
    
    # Pydantic v2: configuración del modelo
    model_config = ConfigDict(
        populate_by_name=True,
        protected_namespaces=()
    )


class ParsedModel(BaseModel):
    """Modelo parseado del Model_Description"""
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    capacity: Optional[str] = None
    ram: Optional[str] = None
    country: Optional[str] = None
    full_model: Optional[str] = None


class SupabaseIds(BaseModel):
    """IDs de registros creados en Supabase"""
    product_id: Optional[int] = None
    variant_id: Optional[int] = None
    item_id: Optional[int] = None
    product_number: Optional[str] = None
    message: Optional[str] = None


class QueryDeviceResponse(BaseModel):
    """Respuesta exitosa de consulta de dispositivo"""
    success: bool = True
    data: Dict[str, Any]
    balance: Optional[float] = None
    price: Optional[float] = None
    order_id: Optional[str] = None
    sheet_updated: Optional[bool] = None
    total_registros: Optional[int] = None
    sheet_url: Optional[str] = None
    sheet_error: Optional[str] = None
    supabase_saved: Optional[bool] = None
    supabase_ids: Optional[SupabaseIds] = None
    supabase_error: Optional[str] = None
    parsed_model: Optional[ParsedModel] = None
    product_price: Optional[float] = None
    product_currency: Optional[str] = None


class ErrorResponse(BaseModel):
    """Respuesta de error genérica"""
    success: bool = False
    error: str


class BalanceResponse(BaseModel):
    """Respuesta de balance"""
    success: bool
    balance: Optional[float] = None
    message: Optional[str] = None


class Service(BaseModel):
    """Información de un servicio"""
    id: str
    name: str
    price: Optional[str] = None


class ServicesResponse(BaseModel):
    """Respuesta con lista de servicios"""
    success: bool
    services: Optional[List[Dict[str, Any]]] = None
    total: Optional[int] = None
    message: Optional[str] = None
    all_services: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class HistoryRequest(BaseModel):
    """Solicitud para buscar en historial"""
    imei_o_order_id: str = Field(
        ...,
        description="IMEI u Order ID a buscar",
        json_schema_extra={"example": "356789012345678"}
    )
    formato: str = Field(
        default="beta",
        description="Formato de respuesta",
        json_schema_extra={"example": "beta"}
    )


class HistoryResponse(BaseModel):
    """Respuesta de búsqueda en historial"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None


# ============ SHEETS ENDPOINTS ============

class StatsResponse(BaseModel):
    """Respuesta de estadísticas del sheet"""
    success: bool
    total_consultas: Optional[int] = None
    ultima_consulta: Optional[str] = None
    sheet_url: Optional[str] = None
    sheet_existe: Optional[bool] = None
    error: Optional[str] = None


class SheetUrlResponse(BaseModel):
    """Respuesta con URL del sheet"""
    url: Optional[str] = None
    sheet_id: str
    error: Optional[str] = None


# ============ RENIEC ENDPOINTS ============

class ReniecDNIRequest(BaseModel):
    """Solicitud para consultar DNI en RENIEC"""
    numero: str = Field(
        ...,
        description="Número de DNI a consultar",
        min_length=8,
        max_length=8,
        json_schema_extra={"example": "46027897"}
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "numero": "46027897"
                }
            ]
        }
    )


class ReniecDNIResponse(BaseModel):
    """Respuesta de consulta DNI en RENIEC"""
    first_name: str = Field(..., description="Nombres")
    first_last_name: str = Field(..., description="Apellido paterno")
    second_last_name: str = Field(..., description="Apellido materno")
    full_name: str = Field(..., description="Nombre completo")
    document_number: str = Field(..., description="Número de DNI")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "first_name": "ROXANA KARINA",
                    "first_last_name": "DELGADO",
                    "second_last_name": "CUELLAR",
                    "full_name": "DELGADO CUELLAR ROXANA KARINA",
                    "document_number": "46027896"
                }
            ]
        }
    )


# ============ HEALTH CHECK ============

class HealthResponse(BaseModel):
    """Respuesta de health check"""
    status: str
    message: str
    api_provider: Optional[str] = None
    timestamp: Optional[str] = None
