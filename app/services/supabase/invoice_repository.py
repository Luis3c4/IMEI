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
    
    def create_invoice(self, invoice_number: str, invoice_date: str, customer_id: Optional[int] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea una nueva factura en la base de datos.
        El customer_number se genera automáticamente en la BD mediante trigger.
        
        Args:
            invoice_number: Número de factura generado por el frontend (ej: "MA85377130")
            invoice_date: Fecha de la factura (ej: "September 04, 2025")
            customer_id: ID del cliente (FK a customers.id). None para facturas sin relación.
            user_id: UUID del usuario autenticado (FK a auth.users.id). None para facturas legacy.
            
        Returns:
            Dict con success, data (incluyendo customer_number generado automáticamente) o error
        """
        if not self.client:
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
            
            response = self.client.table('invoices').insert(invoice_data).execute()
            
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
    
    def get_invoice_by_number(self, invoice_number: str) -> Dict[str, Any]:
        """
        Busca una factura por su número (identificador único).
        
        Args:
            invoice_number: Número de factura (ej: "MA85377130")
            
        Returns:
            Dict con success, data o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = self.client.table('invoices').select('*').eq(
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
    
    def get_invoices_by_customer_number(self, customer_number: str) -> Dict[str, Any]:
        """
        Obtiene todas las facturas asociadas a un customer_number.
        
        Args:
            customer_number: Número de cliente (ej: "90000001")
            
        Returns:
            Dict con success, data (lista de facturas) o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = self.client.table('invoices').select('*').eq(
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
    
    def get_invoices_by_customer_id(self, customer_id: int) -> Dict[str, Any]:
        """
        Obtiene todas las facturas asociadas a un customer_id.
        
        Args:
            customer_id: ID del cliente (FK a customers.id)
            
        Returns:
            Dict con success, data (lista de facturas) o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = self.client.table('invoices').select('*').eq(
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
    
    def get_all_invoices(self, limit: int = 100) -> Dict[str, Any]:
        """
        Obtiene todas las facturas (últimas N).
        
        Args:
            limit: Número máximo de facturas a retornar (default 100)
            
        Returns:
            Dict con success, data (lista de facturas) o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = self.client.table('invoices').select('*').order(
                'created_at', desc=True
            ).limit(limit).execute()
            
            return {'success': True, 'data': response.data or []}
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo facturas: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_invoice_products(self, invoice_id: int, products_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crea los productos asociados a una factura.
        Requiere que product_id y variant_id vengan en la request.
        
        Args:
            invoice_id: ID de la factura (FK a invoices.id)
            products_list: Lista de productos a guardar. Cada producto DEBE contener:
                - product_id: ID del producto (REQUERIDO)
                - variant_id: ID del variant (opcional)
                - serial_number: Número de serie/IMEI (opcional)
                - quantity: Cantidad (default: 1)
                - item_price: Precio unitario (unit_price)
                - extended_price: Precio extendido (unit_price * quantity)
                
        Returns:
            Dict con success, data (lista de productos creados) o error
        """
        if not self.client:
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
                    'quantity': product.get('quantity', 1),
                    'unit_price': product.get('item_price', 0),
                    'extended_price': product.get('extended_price', 0),
                    'serial_number': product.get('serial_number')
                }
                invoice_products_data.append(product_data)
            
            # Insertar todos los productos en una sola operación
            response = self.client.table('invoice_products').insert(invoice_products_data).execute()
            
            if not response.data:
                return {'success': False, 'error': 'No se pudieron crear los productos de la factura'}
            
            logger.info(f"✅ {len(response.data)} productos agregados a factura ID {invoice_id}")
            return {'success': True, 'data': response.data}
            
        except Exception as e:
            logger.error(f"❌ Error creando productos de factura: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_invoice_with_products(self, invoice_id: int) -> Dict[str, Any]:
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
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            # Obtener la factura
            invoice_response = self.client.table('invoices').select('*').eq('id', invoice_id).execute()
            
            if not invoice_response.data:
                return {'success': False, 'error': f'Factura con ID {invoice_id} no encontrada'}
            
            invoice = invoice_response.data[0]
            
            # Obtener los productos con JOINs a products y product_variants
            products_response = self.client.table('invoice_products').select(
                '*,' 
                'products(id, name, category),' 
                'product_variants(id, color, capacity, price)'
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
                
                product_info = {
                    'id': item.get('id'),
                    'quantity': item.get('quantity'),
                    'unit_price': item.get('unit_price'),
                    'extended_price': item.get('extended_price'),
                    'serial_number': item.get('serial_number'),
                    # Datos de JOIN (product_id es requerido, siempre existe)
                    'name': products_dict.get('name'),
                    'category': products_dict.get('category'),
                    'color': variants_dict.get('color'),
                    'capacity': variants_dict.get('capacity'),
                    'current_price': variants_dict.get('price')
                }
                products.append(product_info)
            
            result = {
                'invoice': invoice,
                'products': products
            }
            
            logger.info(f"✅ Factura ID {invoice_id} obtenida con {len(products)} productos")
            return {'success': True, 'data': result}
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo factura con productos: {str(e)}")
            return {'success': False, 'error': str(e)}

