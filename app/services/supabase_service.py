"""
Servicio para manejar todas las interacciones con Supabase
Base de datos PostgreSQL con API REST/GraphQL
"""

import logging
from typing import Dict, Any, List, Optional
from ..config import settings

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("Instala supabase-py: pip install supabase")

logger = logging.getLogger(__name__)


class SupabaseService:
    """Servicio para manejar operaciones con Supabase"""
    
    def __init__(self):
        """Inicializa la conexión con Supabase"""
        self.client: Optional[Client] = None
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("⚠️  Credenciales de Supabase no configuradas")
            return
        
        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("✅ Conexión con Supabase establecida")
        except Exception as e:
            logger.error(f"❌ Error al conectar con Supabase: {str(e)}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Verifica si está conectado a Supabase"""
        return self.client is not None
    
    # ==================== TABLA: DEVICES ====================
    
    def insert_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inserta un nuevo dispositivo en la BD"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table('devices').insert(
                device_data
            ).execute()
            
            logger.info(f"✅ Dispositivo insertado: {device_data.get('imei')}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al insertar dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_device(self, imei: str) -> Dict[str, Any]:
        """Obtiene un dispositivo por IMEI"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table('devices').select(
                "*"
            ).eq("imei", imei).execute()
            
            if response.data:
                return {'success': True, 'data': response.data[0]}
            return {'success': False, 'error': 'Dispositivo no encontrado'}
        except Exception as e:
            logger.error(f"❌ Error al obtener dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_device(self, imei: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza un dispositivo"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table('devices').update(
                device_data
            ).eq("imei", imei).execute()
            
            logger.info(f"✅ Dispositivo actualizado: {imei}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al actualizar dispositivo: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def list_devices(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Lista todos los dispositivos"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table('devices').select(
                "*"
            ).range(offset, offset + limit - 1).execute()
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al listar dispositivos: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}
    
    # ==================== TABLA: CONSULTA_HISTORY ====================
    
    def insert_history(self, history_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inserta un registro de consulta en el historial"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            response = self.client.table('consulta_history').insert(
                history_data
            ).execute()
            
            logger.info(f"✅ Consulta registrada: {history_data.get('imei')}")
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al registrar consulta: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_device_history(self, imei: str, limit: int = 50) -> Dict[str, Any]:
        """Obtiene el historial de consultas de un dispositivo"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table('consulta_history').select(
                "*"
            ).eq("imei", imei).order("created_at", desc=True).limit(limit).execute()
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error al obtener historial: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}
    
    # ==================== OPERACIONES GENÉRICAS ====================
    
    def raw_query(self, table: str, operation: str = "select", **kwargs) -> Dict[str, Any]:
        """Ejecuta una operación genérica en una tabla"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        try:
            if operation == "select":
                response = self.client.table(table).select(kwargs.get("columns", "*")).execute()  # type: ignore
            elif operation == "insert":
                response = self.client.table(table).insert(kwargs.get("data", {})).execute()  # type: ignore
            elif operation == "update":
                response = self.client.table(table).update(kwargs.get("data", {})).execute()  # type: ignore
            elif operation == "delete":
                response = self.client.table(table).delete().execute()  # type: ignore
            else:
                return {'success': False, 'error': f'Operación no soportada: {operation}'}
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"❌ Error en operación {operation}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # ==================== TABLA: PRODUCTS ==================== 
    def get_products_with_variants(self) -> Dict[str, Any]:
        """Obtiene todos los productos con sus variantes y sus items"""
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table('products').select(
                f"""
                *,
                product_variants (
                    id,
                    color,
                    capacity,
                    price,
                    product_items (
                        id,
                        serial_number,
                        status
                    )
                )
                """
            ).execute()

            products: List[Dict[str, Any]] = response.data or []
            for product in products:
                variants = product.get('product_variants') or []
                for variant in variants:
                    items = variant.get('product_items') or []
                    # Contar solo items disponibles
                    available_items = [item for item in items if item.get('status') == 'available']
                    variant['quantity'] = len(available_items)
                    variant['serial_numbers'] = [item.get('serial_number') for item in available_items if item.get('serial_number')]
            
            logger.info(f"Productos con variantes obtenidos: {len(products)} productos")
            return {'success': True, 'data': products, 'count': len(products)}
        except Exception as e:
            logger.error(f"Error al obtener productos con variantes: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}
    
    def save_device_query(self, device_info: Dict[str, Any], metadata: Dict[str, Any], parsed_model: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        Guarda un dispositivo consultado con toda su información relacionada
        
        Args:
            device_info: Datos del dispositivo desde DHRU
            metadata: Metadata adicional (order_id, price, etc)
            parsed_model: Información parseada del Model_Description
            
        Returns:
            {'success': bool, 'product_id': int, 'variant_id': int, 'item_id': int}
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        
        try:
            # 1. BUSCAR O CREAR PRODUCTO
            product_name = parsed_model.get('full_model') or device_info.get('Model_Description', 'Unknown')
            
            # Buscar si el producto ya existe
            product_response = self.client.table('products').select('*').eq('name', product_name).execute()
            
            if product_response.data:
                product_id = product_response.data[0]['id']
                logger.info(f"✅ Producto existente encontrado: {product_name} (ID: {product_id})")
            else:
                # Crear nuevo producto
                product_data = {
                    'name': product_name,
                    'category': parsed_model.get('brand', 'Unknown'),
                    'description': device_info.get('Model_Description')
                }
                new_product = self.client.table('products').insert(product_data).execute()
                product_id = new_product.data[0]['id']
                logger.info(f"✅ Nuevo producto creado: {product_name} (ID: {product_id})")
            
            # 2. BUSCAR O CREAR VARIANTE (color + capacidad)
            color = parsed_model.get('color') or 'Unknown'
            capacity = parsed_model.get('capacity') or 'Unknown'
            
            variant_response = self.client.table('product_variants').select('*').eq(
                'product_id', product_id
            ).eq('color', color).eq('capacity', capacity).execute()
            
            if variant_response.data:
                variant_id = variant_response.data[0]['id']
                logger.info(f"✅ Variante existente: {color} {capacity} (ID: {variant_id})")
            else:
                # Crear nueva variante con precio del metadata
                variant_data = {
                    'product_id': product_id,
                    'color': color,
                    'capacity': capacity,
                    'price': metadata.get('price', 0.0)
                }
                new_variant = self.client.table('product_variants').insert(variant_data).execute()
                variant_id = new_variant.data[0]['id']
                logger.info(f"✅ Nueva variante creada: {color} {capacity} (ID: {variant_id})")
            
            # 3. CREAR PRODUCT_ITEM (Serial Number único)
            serial_number = device_info.get('Serial_Number') or device_info.get('IMEI', 'Unknown')
            
            # Verificar si ya existe este serial
            existing_item = self.client.table('product_items').select('*').eq(
                'serial_number', serial_number
            ).execute()
            
            if existing_item.data:
                logger.warning(f"⚠️  Serial number ya existe: {serial_number}")
                item_id = existing_item.data[0]['id']
            else:
                item_data = {
                    'variant_id': variant_id,
                    'serial_number': serial_number,
                    'status': 'available'  # Puedes ajustar según el iCloud_Lock u otro criterio
                }
                new_item = self.client.table('product_items').insert(item_data).execute()
                item_id = new_item.data[0]['id']
                logger.info(f"✅ Product item creado: {serial_number} (ID: {item_id})")
            
            return {
                'success': True,
                'product_id': product_id,
                'variant_id': variant_id,
                'item_id': item_id,
                'message': 'Dispositivo guardado correctamente'
            }
            
        except Exception as e:
            logger.error(f"❌ Error guardando dispositivo en Supabase: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_product_item_status(self, item_id: int, new_status: str) -> Dict[str, Any]:
        """
        Actualiza el status de un product_item
        
        Args:
            item_id: ID del product_item
            new_status: Nuevo status ('available', 'sold', 'reserved', etc.)
            
        Returns:
            {'success': bool, 'data': dict}
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        
        try:
            # Validar status permitidos
            valid_statuses = ['available', 'sold', 'reserved']
            if new_status not in valid_statuses:
                return {
                    'success': False, 
                    'error': f'Status inválido. Debe ser uno de: {valid_statuses}'
                }
            
            response = self.client.table('product_items').update({
                'status': new_status
            }).eq('id', item_id).execute()
            
            if not response.data:
                return {'success': False, 'error': 'Product item no encontrado'}
            
            logger.info(f"✅ Status actualizado para item {item_id}: {new_status}")
            return {'success': True, 'data': response.data[0]}
            
        except Exception as e:
            logger.error(f"❌ Error actualizando status: {str(e)}")
            return {'success': False, 'error': str(e)}

# Instancia global del servicio
supabase_service = SupabaseService()
