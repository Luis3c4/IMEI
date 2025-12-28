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


# ============ HEALTH CHECK ============

class HealthResponse(BaseModel):
    """Respuesta de health check"""
    status: str
    message: str
    api_provider: Optional[str] = None
    timestamp: Optional[str] = None
