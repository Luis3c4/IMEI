"""
ProductRepository - Gestión de productos, variantes e items
Maneja las tablas: products, product_variants, product_items
Incluye el método complejo save_device_query para guardar dispositivos consultados
"""

import logging
from typing import Dict, Any, Optional, List
from collections import defaultdict
from .base import BaseSupabaseRepository
from app.config.pricing_pnumbers import get_static_product_number
from app.utils.parsers import clean_apple_watch_model
from app.utils.colors import get_color_hex, get_color_info
from app.utils.formatters import format_date_spanish

logger = logging.getLogger(__name__)


class ProductRepository(BaseSupabaseRepository):
    """Repositorio para operaciones relacionadas con productos e inventario"""
    
    def get_products_with_variants(self) -> Dict[str, Any]:
        """
        Obtiene todos los productos con sus variantes y items asociados.
        Incluye conteo de items disponibles y sus serial numbers.
        
        Returns:
            Dict con success, data (lista de productos con variantes anidadas), count
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado', 'data': []}
        
        assert self.client is not None
        try:
            response = self.client.table('products').select(
                """
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
        Guarda un dispositivo consultado con toda su información relacionada.
        Método complejo que maneja la creación/actualización de:
        - Product (tabla products)
        - Product Variant (tabla product_variants)
        - Product Item (tabla product_items)
        
        Args:
            device_info: Datos del dispositivo desde DHRU (Model, Serial_Number, IMEI, etc)
            metadata: Metadata adicional
                     - service_id: ID del servicio DHRU usado (219 o 30)
                     - price: Precio de la consulta DHRU
                     - product_price: Precio del producto (opcional)
                     - product_number: Product Number desde DHRU (opcional)
            parsed_model: Información parseada del Model_Description
                         - full_model, brand, color, capacity, ram
            
        Returns:
            Dict con success, product_id, variant_id, item_id, product_number, message
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        
        try:
            # 1. BUSCAR O CREAR PRODUCTO
            # Determinar qué usar como nombre del producto según el servicio DHRU usado
            service_id = metadata.get('service_id', '30')
            
            raw_model = device_info.get('Model')
            clean_device_model = clean_apple_watch_model(raw_model)

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
                assert isinstance(variant_data_item, dict)
                variant_id = variant_data_item['id']  # type: ignore
                color_display = color if color else 'NULL'
                capacity_display = capacity_combined if capacity_combined else 'NULL'
                logger.info(f"✅ Variante existente: {color_display} {capacity_display} (ID: {variant_id})")
                
                # Actualizar model_description si es necesario
                model_description = device_info.get('Model_Description')
                if model_description and model_description != variant_data_item.get('model_description'):
                    self.client.table('product_variants').update({
                        'model_description': model_description
                    }).eq('id', variant_id).execute()
                    logger.info(f"✅ Model description actualizado para variante {variant_id}")
            else:
                # Crear nueva variante con precio del producto o precio de consulta
                # Prioridad: product_price > price (consulta DHRU)
                product_price = metadata.get('product_price') or metadata.get('price', 0.0)
                variant_data = {
                    'product_id': product_id,
                    'color': color,
                    'capacity': capacity_combined,
                    'price': product_price,
                    'model_description': device_info.get('Model_Description')
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
                
                # Actualizar product_number si es necesario
                update_data = {}
                if product_number:
                    update_data['product_number'] = product_number
                
                if update_data:
                    self.client.table('product_items').update(update_data).eq('id', item_id).execute()
                    logger.info(f"✅ Datos actualizados para item {item_id}: {', '.join(update_data.keys())}")
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
                'product_number': product_number,
                'message': 'Dispositivo guardado correctamente'
            }
            
        except Exception as e:
            logger.error(f"❌ Error guardando dispositivo en Supabase: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_product_item_status(self, item_id: int, new_status: str) -> Dict[str, Any]:
        """
        Actualiza el status de un product_item (available, sold)
        
        Args:
            item_id: ID del product_item
            new_status: Nuevo status ('available', 'sold')
            
        Returns:
            Dict con success, data o error
        """
        if not self.is_connected():
            return {'success': False, 'error': 'Supabase no conectado'}
        
        assert self.client is not None
        
        try:
            # Validar status permitidos
            valid_statuses = ['available', 'sold']
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
    
    def get_products_hierarchical(
        self, 
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene todos los productos con estructura jerárquica de 3 niveles:
        - Fase 1: Producto agrupado con todos los colores y capacidades
        - Fase 2: Agrupación por capacidad con colores disponibles
        - Fase 3: Items individuales con detalles completos
        
        Solo retorna items con status='available'.
        
        Args:
            category: Filtro opcional por categoría (ej: 'IPHONE', 'MACBOOK')
            
        Returns:
            Dict con success, data (productos jerárquicos), count
        """
        if not self.is_connected():
            return {
                'success': False, 
                'error': 'Supabase no conectado', 
                'data': [],
                'count': 0
            }
        
        assert self.client is not None
        
        try:
            # Construir query base con nested select
            query = self.client.table('products').select(
                """
                id,
                name,
                category,
                created_at,
                updated_at,
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
                        product_number,
                        created_at
                    )
                )
                """
            )
            
            # Aplicar filtro de categoría si se especifica
            if category:
                query = query.eq('category', category.upper())
            
            # Ordenar por nombre
            query = query.order('name', desc=False)
            
            response = query.execute()
            
            if not response.data:
                return {
                    'success': True,
                    'data': [],
                    'count': 0
                }
            
            # Procesar cada producto
            hierarchical_products = []
            
            for product in response.data:
                if not isinstance(product, dict):
                    continue
                
                product_id = product.get('id')
                product_name = product.get('name', 'Unknown')
                product_category = product.get('category')
                variants = product.get('product_variants', [])
                
                if not isinstance(variants, list):
                    continue
                
                # Estructuras para agregar datos
                all_colors_set = set()  # Todos los colores del producto
                all_capacities_set = set()  # Todas las capacidades del producto
                capacity_groups_dict: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
                    'items': [],
                    'colors_set': set(),
                    'variant_id': None
                })
                total_quantity = 0
                latest_date = None
                
                # Procesar cada variante
                for variant in variants:
                    if not isinstance(variant, dict):
                        continue
                    
                    variant_id = variant.get('id')
                    color = str(variant.get('color')) if variant.get('color') is not None else None
                    capacity = str(variant.get('capacity')) if variant.get('capacity') is not None else None
                    items = variant.get('product_items', [])
                    
                    if not isinstance(items, list):
                        continue
                    
                    # Filtrar solo items disponibles
                    available_items = [
                        item for item in items 
                        if isinstance(item, dict) and item.get('status') == 'available'
                    ]
                    
                    if not available_items:
                        continue  # Saltar variantes sin items disponibles
                    
                    # Agregar color al set global (si existe)
                    if color:
                        all_colors_set.add(color)
                    
                    # Agregar capacidad al set global
                    all_capacities_set.add(capacity)  # Puede ser None
                    
                    # Clave para agrupar por capacidad (usar string "null" para None)
                    capacity_key: str = capacity if capacity is not None else "null"
                    
                    # Inicializar grupo si no existe
                    if capacity_groups_dict[capacity_key]['variant_id'] is None:
                        capacity_groups_dict[capacity_key]['variant_id'] = variant_id
                    
                    # Agregar color al grupo de capacidad (si existe)
                    if color:
                        capacity_groups_dict[capacity_key]['colors_set'].add(color)
                    
                    # Procesar cada item disponible
                    for item in available_items:
                        serial = str(item.get('serial_number', ''))
                        product_number = str(item.get('product_number')) if item.get('product_number') else None
                        item_created_at = str(item.get('created_at')) if item.get('created_at') else None
                        
                        # Actualizar fecha más reciente
                        if item_created_at:
                            if latest_date is None or item_created_at > str(latest_date):
                                latest_date = item_created_at
                        
                        # Crear detalle del item
                        item_detail = {
                            'serial': serial,
                            'productNumber': product_number,
                            'capacity': capacity,
                            'color': color or 'UNKNOWN',
                            'colorHex': get_color_hex(color)
                        }
                        
                        capacity_groups_dict[capacity_key]['items'].append(item_detail)
                        total_quantity += 1
                
                # Si el producto no tiene items disponibles, saltar
                if total_quantity == 0:
                    continue
                
                # Convertir sets a listas con info de colores
                all_colors_list = [
                    get_color_info(color) for color in sorted(all_colors_set)
                ]
                
                # Convertir capacidades a lista (mantener None como None)
                all_capacities_list = sorted(
                    [cap for cap in all_capacities_set if cap is not None]
                ) + ([None] if None in all_capacities_set else [])
                
                # Construir capacity_groups
                capacity_groups_list = []
                for capacity_key, group_data in capacity_groups_dict.items():
                    # Convertir colores del grupo
                    group_colors = [
                        get_color_info(color) 
                        for color in sorted(group_data['colors_set'])
                    ]
                    
                    capacity_value = None if capacity_key == "null" else capacity_key
                    
                    capacity_group = {
                        'id': group_data['variant_id'],
                        'capacity': capacity_value,
                        'quantity': len(group_data['items']),
                        'colors': group_colors,
                        'items': group_data['items']
                    }
                    capacity_groups_list.append(capacity_group)
                
                # Ordenar grupos por capacidad (null al final)
                capacity_groups_list.sort(
                    key=lambda x: (x['capacity'] is None, x['capacity'] or '')
                )
                
                # Formatear fecha de actualización
                last_update_str = format_date_spanish(latest_date)
                
                # Construir producto jerárquico
                hierarchical_product = {
                    'id': product_id,
                    'name': product_name,
                    'totalQuantity': total_quantity,
                    'capacities': all_capacities_list,
                    'colors': all_colors_list,
                    'lastUpdate': last_update_str,
                    'capacityGroups': capacity_groups_list
                }
                
                hierarchical_products.append(hierarchical_product)
            
            logger.info(
                f"✅ Productos jerárquicos obtenidos: {len(hierarchical_products)} productos con stock disponible"
            )
            
            return {
                'success': True,
                'data': hierarchical_products,
                'count': len(hierarchical_products)
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo productos jerárquicos: {str(e)}")
            return {
                'success': False, 
                'error': str(e), 
                'data': [],
                'count': 0
            }
