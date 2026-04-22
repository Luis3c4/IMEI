"""
InvoiceRepository - Gestión de facturas
Maneja las tablas: invoices, invoice_products
"""

import logging
from typing import Dict, Any, Optional, List
from .base import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class InvoiceRepository(BaseSupabaseRepository):
    """Repositorio para operaciones relacionadas con facturas"""
    
    async def create_invoice(
        self,
        invoice_number: str,
        invoice_date: str,
        customer_id: Optional[int] = None,
        user_id: Optional[str] = None,
        order_number: Optional[str] = None,
        shipping_agency: Optional[str] = None,
        shipping_department: Optional[str] = None,
        shipping_province: Optional[str] = None,
        bank_name: Optional[str] = None,
        payment_total: Optional[float] = None,
        payment_holder: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Crea una nueva factura en la base de datos.
        El customer_number se genera automáticamente en la BD mediante trigger.
        
        Args:
            invoice_number: Número de factura generado por el frontend (ej: "MA85377130")
            invoice_date: Fecha de la factura (ej: "September 04, 2025")
            customer_id: ID del cliente (FK a customers.id). None para facturas sin relación.
            user_id: UUID del usuario autenticado (FK a auth.users.id). None para facturas legacy.
            order_number: Número de orden generado por el frontend (ej: "W1351042737").
            shipping_agency: Agencia de envio (ej: "OFICINA" u "OLVA").
            shipping_department: Departamento de envio (solo aplica para OLVA).
            shipping_province: Provincia de envio (solo aplica para OLVA).
            bank_name: Banco usado para el pago.
            payment_total: Monto total pagado.
            payment_holder: Titular del pago.
            
        Returns:
            Dict con success, data (incluyendo customer_number generado automáticamente) o error
        """
        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            invoice_data: Dict[str, Any] = {
                'invoice_number': invoice_number.strip(),
                'invoice_date': invoice_date.strip()
                # customer_number se genera automáticamente por trigger
            }
            
            # Agregar customer_id solo si se proporciona
            if customer_id is not None:
                invoice_data['customer_id'] = customer_id
            
            # Agregar user_id solo si se proporciona
            if user_id is not None:
                invoice_data['user_id'] = user_id
            
            # Agregar order_number solo si se proporciona
            if order_number is not None:
                invoice_data['order_number'] = order_number.strip()

            # Campos opcionales de pago/envio
            if shipping_agency is not None:
                invoice_data['shipping_agency'] = shipping_agency.strip()
            if shipping_department is not None:
                invoice_data['shipping_department'] = shipping_department.strip()
            if shipping_province is not None:
                invoice_data['shipping_province'] = shipping_province.strip()
            if bank_name is not None:
                invoice_data['bank_name'] = bank_name.strip()
            if payment_total is not None:
                invoice_data['payment_total'] = payment_total
            if payment_holder is not None:
                invoice_data['payment_holder'] = payment_holder.strip()
            
            response = await client.table('invoices').insert(invoice_data).execute()
            
            if not response.data:
                return {'success': False, 'error': 'No se pudo crear la factura'}
            
            invoice = response.data[0]  # type: ignore
            assert isinstance(invoice, dict)
            logger.info(
                f"✅ Factura creada: {invoice['invoice_number']} "
                f"(customer_number: {invoice['customer_number']})"
            )
            return {'success': True, 'data': invoice}
            
        except Exception as e:
            logger.error(f"❌ Error creando factura: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_invoice_by_number(self, invoice_number: str) -> Dict[str, Any]:
        """
        Busca una factura por su número (identificador único).
        
        Args:
            invoice_number: Número de factura (ej: "MA85377130")
            
        Returns:
            Dict con success, data o error
        """
        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = await client.table('invoices').select('*').eq(
                'invoice_number', invoice_number.strip()
            ).execute()
            
            if not response.data:
                return {
                    'success': False, 
                    'error': f'Factura {invoice_number} no encontrada'
                }
            
            return {'success': True, 'data': response.data[0]}
            
        except Exception as e:
            logger.error(f"❌ Error buscando factura por número: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_invoices_by_customer_number(self, customer_number: str) -> Dict[str, Any]:
        """
        Obtiene todas las facturas asociadas a un customer_number.
        
        Args:
            customer_number: Número de cliente (ej: "90000001")
            
        Returns:
            Dict con success, data (lista de facturas) o error
        """
        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = await client.table('invoices').select('*').eq(
                'customer_number', customer_number
            ).order('created_at', desc=True).execute()
            
            if not response.data:
                return {
                    'success': False, 
                    'error': f'No se encontraron facturas para customer_number {customer_number}'
                }
            
            return {'success': True, 'data': response.data}
            
        except Exception as e:
            logger.error(f"❌ Error buscando facturas por customer_number: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_invoices_by_customer_id(self, customer_id: int) -> Dict[str, Any]:
        """
        Obtiene todas las facturas asociadas a un customer_id.
        
        Args:
            customer_id: ID del cliente (FK a customers.id)
            
        Returns:
            Dict con success, data (lista de facturas) o error
        """
        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = await client.table('invoices').select('*').eq(
                'customer_id', customer_id
            ).order('created_at', desc=True).execute()
            
            if not response.data:
                return {
                    'success': False, 
                    'error': f'No se encontraron facturas para customer_id {customer_id}'
                }
            
            return {'success': True, 'data': response.data}
            
        except Exception as e:
            logger.error(f"❌ Error buscando facturas por customer_id: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_all_invoices(self, limit: int = 100) -> Dict[str, Any]:
        """
        Obtiene todas las facturas (últimas N).
        
        Args:
            limit: Número máximo de facturas a retornar (default 100)
            
        Returns:
            Dict con success, data (lista de facturas) o error
        """
        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = await client.table('invoices').select('*').order(
                'created_at', desc=True
            ).limit(limit).execute()
            
            return {'success': True, 'data': response.data or []}
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo facturas: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_historial_invoices(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Obtiene facturas paginadas con datos anidados de cliente y productos
        para la tabla de historial (Quantum).

        Args:
            page: Número de página (1-based).
            page_size: Registros por página (default 20).

        Returns:
            Dict con success, data, total, page, page_size, total_pages o error
        """
        import math
        from postgrest.types import CountMethod

        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}

        try:
            offset = (page - 1) * page_size

            response = await client.table('invoices').select(
                'id, invoice_date, shipping_agency, shipping_department, shipping_province, '
                'bank_name, payment_total, payment_holder, '
                'customers(name, dni, phone), '
                'invoice_products('
                '  id, unit_price, extended_price, '
                '  products(name, category), '
                '  product_variants(color, capacity, chip), '
                '  product_items(serial_number)'
                ')',
                count=CountMethod.exact
            ).order('created_at', desc=True).range(offset, offset + page_size - 1).execute()

            total: int = response.count or 0
            total_pages = math.ceil(total / page_size) if total > 0 else 1

            logger.info(f"✅ Historial: página {page}/{total_pages}, {len(response.data or [])} facturas")
            return {
                'success': True,
                'data': response.data or [],
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo historial de facturas: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def create_invoice_products(self, invoice_id: int, products_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crea los productos asociados a una factura.
        Requiere que product_id venga en la request. product_item_id referencia el item físico vendido.
        
        Args:
            invoice_id: ID de la factura (FK a invoices.id)
            products_list: Lista de productos a guardar. Cada producto DEBE contener:
                - product_id: ID del producto (REQUERIDO)
                - variant_id: ID del variant (opcional)
                - product_item_id: ID del item físico vendido (FK a product_items.id, opcional pero recomendado)
                - quantity: Cantidad (default: 1)
                - item_price: Precio unitario (unit_price)
                - extended_price: Precio extendido (unit_price * quantity)
                
        Returns:
            Dict con success, data (lista de productos creados) o error
        """
        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        if not products_list:
            return {'success': True, 'data': []}  # No hay productos, no es error
        
        try:
            # Preparar datos para inserción
            invoice_products_data = []
            for product in products_list:
                product_id = product.get('product_id')
                
                # Validar que product_id existe
                if not product_id:
                    logger.error(f"❌ Producto sin product_id en factura {invoice_id}")
                    return {'success': False, 'error': 'Todos los productos deben tener product_id'}
                
                # Preparar datos para inserción
                product_data = {
                    'invoice_id': invoice_id,
                    'product_id': product_id,  # REQUERIDO
                    'variant_id': product.get('variant_id'),  # Opcional
                    'product_item_id': product.get('product_item_id'),  # FK a product_items.id
                    'quantity': product.get('quantity', 1),
                    'unit_price': product.get('item_price', 0),
                    'extended_price': product.get('extended_price', 0),
                }
                invoice_products_data.append(product_data)
            
            # Insertar todos los productos en una sola operación
            response = await client.table('invoice_products').insert(invoice_products_data).execute()
            
            if not response.data:
                return {'success': False, 'error': 'No se pudieron crear los productos de la factura'}
            
            logger.info(f"✅ {len(response.data)} productos agregados a factura ID {invoice_id}")
            return {'success': True, 'data': response.data}
            
        except Exception as e:
            logger.error(f"❌ Error creando productos de factura: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_product_items_by_ids(self, item_ids: List[int]) -> Dict[str, Any]:
        """
        Obtiene un mapa {product_item_id: serial_number} para los IDs dados.
        Usado para resolver serial_numbers antes de generar el PDF.
        
        Args:
            item_ids: Lista de IDs de product_items
            
        Returns:
            Dict con success y data={item_id: serial_number}
        """
        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        if not item_ids:
            return {'success': True, 'data': {}}
        
        try:
            response = await client.table('product_items').select('id, serial_number').in_('id', item_ids).execute()
            result = {
                row['id']: row.get('serial_number')
                for row in (response.data or [])
                if isinstance(row, dict) and 'id' in row
            }
            return {'success': True, 'data': result}
        except Exception as e:
            logger.error(f"❌ Error obteniendo product_items por IDs: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def get_invoice_with_products(self, invoice_id: int) -> Dict[str, Any]:
        """
        Obtiene una factura con todos sus productos asociados.
        Realiza JOIN con products y product_variants para obtener información completa.
        
        Args:
            invoice_id: ID de la factura
            
        Returns:
            Dict con success y data conteniendo:
                - invoice: Datos de la factura
                - products: Lista de productos con información completa (via JOINs)
        """
        client = await self._get_client()
        if not client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            # Obtener la factura
            invoice_response = await client.table('invoices').select('*').eq('id', invoice_id).execute()
            
            if not invoice_response.data:
                return {'success': False, 'error': f'Factura con ID {invoice_id} no encontrada'}
            
            invoice = invoice_response.data[0]  # type: ignore
            assert isinstance(invoice, dict)
            
            # Obtener los productos con JOINs a products, product_variants y product_items
            products_response = await client.table('invoice_products').select(
                '*,' 
                'products(id, name, category),' 
                'product_variants(id, color, capacity, price),'
                'product_items(id, serial_number, product_number)'
            ).eq('invoice_id', invoice_id).order('id').execute()
            
            # Procesar datos para formato más legible
            products = []
            for item in products_response.data or []:
                # Validate that item is a dictionary
                if not isinstance(item, dict):
                    logger.warning(f"⚠️ Skipping invalid invoice product item: {item}")
                    continue
                
                products_data = item.get('products')
                products_dict = products_data if isinstance(products_data, dict) else {}
                
                variants_data = item.get('product_variants')
                variants_dict = variants_data if isinstance(variants_data, dict) else {}
                
                item_data = item.get('product_items')
                item_dict = item_data if isinstance(item_data, dict) else {}
                
                product_info = {
                    'id': item.get('id'),
                    'product_item_id': item.get('product_item_id'),
                    'quantity': item.get('quantity'),
                    'unit_price': item.get('unit_price'),
                    'extended_price': item.get('extended_price'),
                    'serial_number': item_dict.get('serial_number'),  # Resolved via FK JOIN
                    'product_number': item_dict.get('product_number'),  # Resolved via FK JOIN
                    # Datos de JOIN (product_id es requerido, siempre existe)
                    'name': products_dict.get('name'),
                    'category': products_dict.get('category'),
                    'color': variants_dict.get('color'),
                    'capacity': variants_dict.get('capacity'),
                    'current_price': variants_dict.get('price')
                }
                products.append(product_info)

            # Obtener datos del cliente si la factura tiene customer_id
            customer: Dict[str, Any] = {}
            if invoice.get('customer_id'):
                customer_response = await client.table('customers').select(
                    'id, name, dni, phone'
                ).eq('id', invoice['customer_id']).execute()
                if customer_response.data:
                    raw_customer = customer_response.data[0]  # type: ignore
                    assert isinstance(raw_customer, dict)
                    customer = raw_customer

            result = {
                'invoice': invoice,
                'customer': customer,
                'products': products,
            }
            
            logger.info(f"✅ Factura ID {invoice_id} obtenida con {len(products)} productos")
            return {'success': True, 'data': result}
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo factura con productos: {str(e)}")
            return {'success': False, 'error': str(e)}

