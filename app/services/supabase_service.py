"""
Servicio para manejar todas las interacciones con Supabase
Base de datos PostgreSQL con API REST/GraphQL
"""

import logging
import re
from typing import Dict, Any, List, Optional
from app.config import settings

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
        self._init_client()

    @staticmethod
    def _clean_apple_watch_model(name: Optional[str]) -> Optional[str]:
        """Elimina tamaños 41/42/44/45/46/49MM del nombre para guardar limpio."""
        if not name or not isinstance(name, str):
            return name
        cleaned = re.sub(r'\b(41|42|44|45|46|49)\s*MM\b', '', name, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned or name.strip()

    def _init_client(self) -> bool:
        """Intenta inicializar el cliente solo si hay credenciales"""
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            logger.warning("⚠️  Credenciales de Supabase no configuradas")
            self.client = None
            return False

        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
            logger.info("✅ Conexión con Supabase establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error al conectar con Supabase: {str(e)}")
            self.client = None
            return False
    
    def is_connected(self) -> bool:
        """Verifica si está conectado a Supabase"""
        if self.client is not None:
            return True
        # Reintenta la conexión en caso de que el cliente haya quedado en None
        return self._init_client()
    
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
                    model_description,
                    product_items (
                        id,
                        serial_number,
                        status,
                        product_number
                    )
                )
                """
            ).execute()

            products = list(response.data) if response.data else []
            for product in products:
                if not isinstance(product, dict):
                    continue
                variants = product.get('product_variants') or []
                if not isinstance(variants, list):
                    continue
                for variant in variants:
                    if not isinstance(variant, dict):
                        continue
                    items = variant.get('product_items') or []
                    if not isinstance(items, list):
                        continue
                    # Contar solo items disponibles
                    available_items = [item for item in items if isinstance(item, dict) and item.get('status') == 'available']
                    variant['quantity'] = len(available_items)
                    variant['serial_numbers'] = [item.get('serial_number') for item in available_items if isinstance(item, dict) and item.get('serial_number')]
                    variant['product_numbers'] = [item.get('product_number') for item in available_items if isinstance(item, dict) and item.get('product_number')]
            
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
            metadata: Metadata adicional (order_id, price, product_price, etc)
                     - service_id: ID del servicio DHRU usado (219 o 30)
                     - price: Precio de la consulta DHRU
                     - product_price: Precio del producto (opcional)
            parsed_model: Información parseada del Model_Description
            
        Returns:
            {'success': bool, 'product_id': int, 'variant_id': int, 'item_id': int}
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        
        try:
            # 1. BUSCAR O CREAR PRODUCTO
            # Determinar qué usar como nombre del producto según el servicio DHRU usado
            service_id = metadata.get('service_id', '30')
            
            raw_model = device_info.get('Model')
            clean_device_model = self._clean_apple_watch_model(raw_model)

            if service_id == "219":
                # Servicio 219 (IMEI): 
                # Prioridad: Model (limpio) > full_model parseado > Model_Description
                product_name = clean_device_model or parsed_model.get('full_model') or device_info.get('Model_Description', 'Unknown')
                logger.info(f"📱 Servicio 219 - Usando Model/full_model: {product_name}")
            else:
                # Servicio 30 (Serial): usar Model directo desde data (necesario para pricing)
                product_name = clean_device_model or parsed_model.get('full_model') or device_info.get('Model_Description', 'Unknown')
                logger.info(f"📱 Servicio 30 - Usando Model: {product_name}")

            # Buscar si el producto ya existe
            product_response = self.client.table('products').select('*').eq('name', product_name).execute()
            
            if product_response.data and len(product_response.data) > 0:
                product_data_item = product_response.data[0]
                product_id = product_data_item['id']  # type: ignore
                logger.info(f"✅ Producto existente encontrado: {product_name} (ID: {product_id})")
            else:
                # Crear nuevo producto
                product_data = {
                    'name': product_name,
                    'category': parsed_model.get('brand') or None
                }
                new_product = self.client.table('products').insert(product_data).execute()
                if new_product.data and len(new_product.data) > 0:
                    product_id = new_product.data[0]['id']  # type: ignore
                else:
                    raise ValueError('No se pudo crear el producto')
                logger.info(f"✅ Nuevo producto creado: {product_name} (ID: {product_id})")
            
            # 2. BUSCAR O CREAR VARIANTE (color + capacidad)
            color = parsed_model.get('color') or None
            ram = parsed_model.get('ram') or None
            capacity = parsed_model.get('capacity') or None
            
            # Combinar RAM y capacidad en un solo string si ambos existen
            if ram and capacity:
                capacity_combined = f"{ram}/{capacity}"
            elif capacity:
                capacity_combined = capacity
            else:
                capacity_combined = None
            
            # Construir query dinámicamente para manejar NULL
            variant_query = self.client.table('product_variants').select('*').eq('product_id', product_id)
            
            if color is not None:
                variant_query = variant_query.eq('color', color)
            else:
                variant_query = variant_query.is_('color', 'null')
            
            if capacity_combined is not None:
                variant_query = variant_query.eq('capacity', capacity_combined)
            else:
                variant_query = variant_query.is_('capacity', 'null')
            
            variant_response = variant_query.execute()
            
            if variant_response.data and len(variant_response.data) > 0:
                variant_data_item = variant_response.data[0]
                variant_id = variant_data_item['id']  # type: ignore
                color_display = color if color else 'NULL'
                capacity_display = capacity_combined if capacity_combined else 'NULL'
                logger.info(f"✅ Variante existente: {color_display} {capacity_display} (ID: {variant_id})")
            else:
                # Crear nueva variante con precio del producto o precio de consulta
                # Prioridad: product_price > price (consulta DHRU)
                product_price = metadata.get('product_price') or metadata.get('price', 0.0)
                model_description = device_info.get('Model_Description')
                variant_data = {
                    'product_id': product_id,
                    'color': color,
                    'capacity': capacity_combined,
                    'price': product_price,
                    'model_description': model_description
                }
                new_variant = self.client.table('product_variants').insert(variant_data).execute()
                if new_variant.data and len(new_variant.data) > 0:
                    variant_id = new_variant.data[0]['id']  # type: ignore
                else:
                    raise ValueError('No se pudo crear la variante')
                color_display = color if color else 'NULL'
                capacity_display = capacity_combined if capacity_combined else 'NULL'
                logger.info(f"✅ Nueva variante creada: {color_display} {capacity_display} (ID: {variant_id})")
            
            # 3. DETERMINAR PRODUCT NUMBER
            from ..config.pricing_pnumbers import get_static_product_number
            
            # Si viene product_number en metadata (desde DHRU 219), usarlo
            product_number = metadata.get('product_number')
            
            # Si no viene, intentar obtener el estático basado en el modelo parseado
            if not product_number:
                # Asegurar que product_name es un str antes de pasarlo a la función
                safe_product_name = product_name if isinstance(product_name, str) else (str(product_name) if product_name is not None else "")
                if not safe_product_name:
                    logger.info(f"ℹ️  Producto sin nombre válido para buscar Product Number: {product_name}")
                    product_number = None
                else:
                    product_number = get_static_product_number(safe_product_name)
                    if product_number:
                        logger.info(f"✅ Product Number estático asignado: {product_number}")
                    else:
                        logger.info(f"ℹ️  Producto sin Product Number estático: {safe_product_name}")
            
            # 4. CREAR PRODUCT_ITEM (Serial Number único) con product_number
            serial_number = device_info.get('Serial_Number') or device_info.get('IMEI', 'Unknown')
            
            # Verificar si ya existe este serial
            existing_item = self.client.table('product_items').select('*').eq(
                'serial_number', serial_number
            ).execute()
            
            if existing_item.data and len(existing_item.data) > 0:
                logger.warning(f"⚠️  Serial number ya existe: {serial_number}")
                item_data_existing = existing_item.data[0]
                item_id = item_data_existing['id']  # type: ignore
                
                # Actualizar product_number en item si es necesario
                if product_number:
                    self.client.table('product_items').update({'product_number': product_number}).eq('id', item_id).execute()
                    logger.info(f"✅ Product number actualizado para item {item_id}")
                
                # Actualizar model_description en variant si es necesario
                model_description = device_info.get('Model_Description')
                if model_description:
                    self.client.table('product_variants').update({'model_description': model_description}).eq('id', variant_id).execute()
                    logger.info(f"✅ Model description actualizado para variant {variant_id}")
            else:
                item_data = {
                    'variant_id': variant_id,
                    'serial_number': serial_number,
                    'product_number': product_number,
                    'status': 'available'  # Puedes ajustar según el iCloud_Lock u otro criterio
                }
                new_item = self.client.table('product_items').insert(item_data).execute()
                if new_item.data and len(new_item.data) > 0:
                    item_id = new_item.data[0]['id']  # type: ignore
                else:
                    raise ValueError('No se pudo crear el product item')
                logger.info(f"✅ Product item creado: {serial_number} | PN: {product_number or 'N/A'} (ID: {item_id})")
            
            return {
                'success': True,
                'product_id': product_id,
                'variant_id': variant_id,
                'item_id': item_id,
                'product_number': product_number,  # Agregar a respuesta
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
