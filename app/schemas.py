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
    phone: Optional[str] = Field(
        default=None,
        description="Teléfono del cliente (solo si existe en BD)"
    )
    source: Optional[str] = Field(
        default=None, 
        description="Fuente de los datos: 'database' (BD local) o 'api' (API externa)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "first_name": "ROXANA KARINA",
                    "first_last_name": "DELGADO",
                    "second_last_name": "CUELLAR",
                    "full_name": "DELGADO CUELLAR ROXANA KARINA",
                    "document_number": "46027896",
                    "phone": "999 888 777",
                    "source": "database"
                }
            ]
        }
    )


# ============ PRODUCTS HIERARCHY ============

class ColorInfo(BaseModel):
    """Información de un color con su código hexadecimal"""
    name: str = Field(..., description="Nombre del color (ej: SILVER, SPACE BLACK)")
    hex: str = Field(..., description="Código hexadecimal del color (ej: #C0C0C0)")


class ProductItemDetail(BaseModel):
    """Detalle de un item individual de producto (Fase 3)"""
    serial: str = Field(..., description="Serial number del dispositivo")
    productNumber: Optional[str] = Field(None, description="Product Number Apple (ej: MFXG4LL/A)")
    capacity: Optional[str] = Field(None, description="Capacidad del item (ej: 256GB)")
    color: str = Field(..., description="Nombre del color")
    colorHex: Optional[str] = Field(None, description="Código hexadecimal del color")


class CapacityGroup(BaseModel):
    """Agrupación por capacidad con items (Fase 2)"""
    id: int = Field(..., description="ID único del grupo de capacidad")
    capacity: Optional[str] = Field(None, description="Capacidad (ej: 256GB) o null si no aplica")
    quantity: int = Field(..., description="Cantidad de items disponibles en esta capacidad")
    colors: List[ColorInfo] = Field(..., description="Lista de colores disponibles en esta capacidad")
    items: List[ProductItemDetail] = Field(..., description="Lista de items individuales")


class ProductHierarchical(BaseModel):
    """Producto con estructura jerárquica de 3 niveles (Fase 1)"""
    id: int = Field(..., description="ID del producto")
    name: str = Field(..., description="Nombre del producto (ej: IPHONE 17 PRO MAX)")
    totalQuantity: int = Field(..., description="Cantidad total de items disponibles")
    capacities: List[Optional[str]] = Field(..., description="Lista de capacidades disponibles (puede contener null)")
    colors: List[ColorInfo] = Field(..., description="Lista de todos los colores disponibles en el producto")
    lastUpdate: str = Field(..., description="Fecha de última actualización en español (ej: 29 de enero)")
    capacityGroups: List[CapacityGroup] = Field(..., description="Agrupaciones por capacidad con sus items")


class ProductHierarchyResponse(BaseModel):
    """Respuesta del endpoint de inventario jerárquico completo"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    data: List[ProductHierarchical] = Field(..., description="Lista de productos con estructura jerárquica")
    count: int = Field(..., description="Cantidad total de productos con stock disponible")
    page: int = Field(default=1, description="Página (siempre 1, sin paginación)")
    pageSize: int = Field(..., description="Total de productos retornados (igual a count)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "success": True,
                    "data": [
                        {
                            "id": 1,
                            "name": "IPHONE 17 PRO MAX",
                            "totalQuantity": 15,
                            "capacities": ["256GB", "512GB"],
                            "colors": [
                                {"name": "SILVER", "hex": "#C0C0C0"},
                                {"name": "SPACE BLACK", "hex": "#1C1C1E"}
                            ],
                            "lastUpdate": "29 de enero",
                            "capacityGroups": [
                                {
                                    "id": 1,
                                    "capacity": "256GB",
                                    "quantity": 8,
                                    "colors": [{"name": "SILVER", "hex": "#C0C0C0"}],
                                    "items": [
                                        {
                                            "serial": "Y3PYVFVY33",
                                            "productNumber": "MFXG4LL/A",
                                            "capacity": "256GB",
                                            "color": "SILVER",
                                            "colorHex": "#C0C0C0"
                                        }
                                    ]
                                }
                            ]
                        }
                    ],
                    "count": 1,
                    "page": 1,
                    "pageSize": 1
                }
            ]
        }
    )


# ============ PRODUCTS CREATE ============

class ProductCreateRequest(BaseModel):
    """Solicitud para crear producto + variante + item"""
    category: str = Field(..., description="Categoría del producto", min_length=1)
    product_name: str = Field(..., description="Nombre del producto", min_length=1)
    color: Optional[str] = Field(default=None, description="Color de la variante")
    capacity: Optional[str] = Field(default=None, description="Capacidad/Tamaño/Presentación")
    serial_number: str = Field(..., description="Serial Number único", min_length=1)
    product_number: str = Field(..., description="Product Number", min_length=1)


class ProductCreateData(BaseModel):
    """Datos de creación de producto"""
    product_id: int
    variant_id: int
    item_id: int


class ProductCreateResponse(BaseModel):
    """Respuesta de creación de producto"""
    success: bool
    data: Optional[ProductCreateData] = None
    error: Optional[str] = None
    message: Optional[str] = None


# ============ CUSTOMERS ============

class CustomerListItem(BaseModel):
    """Un cliente en el listado"""
    id: int
    name: Optional[str] = None
    dni: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[str] = None
    first_name: Optional[str] = None
    first_last_name: Optional[str] = None
    second_last_name: Optional[str] = None


class CustomerListResponse(BaseModel):
    """Respuesta del listado de clientes"""
    success: bool
    data: List[CustomerListItem] = []
    total: int = 0
    error: Optional[str] = None


# ============ HEALTH CHECK ============

class HealthResponse(BaseModel):
    """Respuesta de health check"""
    status: str
    message: str
    api_provider: Optional[str] = None
    timestamp: Optional[str] = None
