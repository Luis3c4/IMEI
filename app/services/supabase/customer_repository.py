"""
CustomerRepository - Gestión de clientes
Maneja la tabla: customers
"""

import logging
import math
from typing import Dict, Any, Optional
from postgrest.types import CountMethod
from .base import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class CustomerRepository(BaseSupabaseRepository):
    """Repositorio para operaciones relacionadas con clientes"""
    
    def create_customer(self, name: str, dni: str, 
                       phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Crea un nuevo cliente en la base de datos.
        
        Args:
            name: Nombre completo del cliente (requerido)
            dni: DNI del cliente (requerido - identificador único)
            phone: Teléfono del cliente (opcional)
            
        Returns:
            Dict con success, data o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            customer_data = {
                'name': name.strip(),
                'dni': dni.strip()
            }
            
            # Solo agregar phone si no es None y no está vacío
            if phone and phone.strip():
                customer_data['phone'] = phone.strip()
            
            response = self.client.table('customers').insert(customer_data).execute()
            
            if not response.data:
                return {'success': False, 'error': 'No se pudo crear el cliente'}
            
            customer = response.data[0]  # type: ignore
            assert isinstance(customer, dict)
            logger.info(f"✅ Cliente creado: {customer['name']} (DNI: {customer['dni']})")
            return {'success': True, 'data': customer}
            
        except Exception as e:
            logger.error(f"❌ Error creando cliente: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_customer_by_dni(self, dni: str) -> Dict[str, Any]:
        """
        Busca un cliente por su DNI (identificador único principal).
        
        Args:
            dni: DNI del cliente
            
        Returns:
            Dict con success, data o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = self.client.table('customers').select('*').eq(
                'dni', dni.strip()
            ).execute()
            
            if not response.data:
                return {'success': False, 'error': f'Cliente con DNI {dni} no encontrado'}
            
            return {'success': True, 'data': response.data[0]}
            
        except Exception as e:
            logger.error(f"❌ Error buscando cliente por DNI: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    # DEPRECATED: customer_number se movió a la tabla invoices
    # def get_customer_by_number(self, customer_number: str) -> Dict[str, Any]:
    #     """
    #     DEPRECADO: customer_number ahora está en la tabla invoices.
    #     Use InvoiceRepository.get_invoices_by_customer_number() en su lugar.
    #     """
    #     pass

    def get_or_create_customer(self, name: str, dni: str,
                               phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Busca un cliente existente por DNI, o crea uno nuevo si no existe.
        Si el cliente existe pero no tiene teléfono y se proporciona uno, lo actualiza.
        
        Args:
            name: Nombre completo del cliente
            dni: DNI del cliente (requerido - identificador único)
            phone: Teléfono (opcional)
            
        Returns:
            Dict con success, data (cliente existente o nuevo), is_new (bool)
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            # Buscar cliente existente por DNI (identificador único)
            dni_search = self.get_customer_by_dni(dni)
            
            if dni_search['success']:
                existing_customer = dni_search['data']
                
                # Verificar si necesita actualización del teléfono
                needs_phone_update = (
                    not existing_customer.get('phone') or  # phone es NULL o vacío
                    existing_customer.get('phone', '').strip() == ''  # phone es string vacío
                )
                
                if needs_phone_update and phone and phone.strip():
                    # Actualizar el teléfono del cliente existente
                    logger.info(f"🔄 Actualizando teléfono para DNI: {dni}")
                    update_result = self.client.table('customers').update(
                        {'phone': phone.strip()}
                    ).eq('dni', dni.strip()).execute()
                    
                    if update_result.data:
                        existing_customer = update_result.data[0]  # type: ignore
                        assert isinstance(existing_customer, dict)
                        logger.info(f"✅ Teléfono actualizado para DNI: {dni}")
                
                logger.info(f"✅ Cliente encontrado por DNI: {dni}")
                return {
                    'success': True, 
                    'data': existing_customer,
                    'is_new': False
                }
            
            # Cliente no existe, crear uno nuevo
            create_result = self.create_customer(name, dni, phone)
            if create_result['success']:
                logger.info(f"✅ Nuevo cliente creado con DNI: {dni}")
                return {
                    'success': True,
                    'data': create_result['data'],
                    'is_new': True
                }
            
            return create_result
            
        except Exception as e:
            logger.error(f"❌ Error en get_or_create_customer: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_customer_reniec_data(self, dni: str) -> Dict[str, Any]:
        """
        Obtiene los datos de RENIEC de un cliente si existen en la BD.
        Los datos de RENIEC son estáticos y no requieren validación de vigencia.
        
        Args:
            dni: DNI del cliente
            
        Returns:
            Dict con success, data (datos de RENIEC) o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            response = self.client.table('customers').select(
                'dni, first_name, first_last_name, second_last_name, name, phone'
            ).eq('dni', dni.strip()).execute()
            
            if not response.data:
                return {'success': False, 'error': 'Cliente no encontrado'}
            
            customer = response.data[0]  # type: ignore
            assert isinstance(customer, dict)
            
            # Verificar si tiene datos de RENIEC
            if not customer.get('first_name'):
                return {'success': False, 'error': 'Sin datos de RENIEC'}
            
            # Construir respuesta con formato de RENIEC desde las columnas
            reniec_response = {
                'first_name': customer.get('first_name', ''),
                'first_last_name': customer.get('first_last_name', ''),
                'second_last_name': customer.get('second_last_name', ''),
                'full_name': customer.get('name', ''),
                'document_number': customer.get('dni', ''),
                'phone': customer.get('phone', '') or None  # None si vacío
            }
            
            logger.info(f"✅ Datos de RENIEC encontrados en BD para DNI: {dni}")
            return {'success': True, 'data': reniec_response}
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de RENIEC del cliente: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_all_customers(self, search: Optional[str] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        Devuelve la lista paginada de clientes ordenados por índice descendente.
        
        Args:
            search: Texto opcional para filtrar por nombre, DNI o teléfono.
            page: Número de página (1-based, default 1).
            page_size: Registros por página (default 20).
            
        Returns:
            Dict con success, data (lista), total, page, page_size, total_pages o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}

        try:
            query = self.client.table('customers').select(
                'id, name, dni, phone, created_at, first_name, first_last_name, second_last_name,'
                'invoices(invoice_products(products(name)))',
                count=CountMethod.exact
            ).order('id', desc=True)

            # Filtro server-side con ilike multi-columna
            if search:
                term = search.strip()
                query = query.or_(f'name.ilike.%{term}%,dni.ilike.%{term}%,phone.ilike.%{term}%')

            # Paginación server-side
            offset = (page - 1) * page_size
            query = query.range(offset, offset + page_size - 1)

            response = query.execute()

            customers: list = response.data or []
            total: int = response.count or 0

            # Extraer nombres de productos únicos por cliente
            for customer in customers:
                invoices = customer.pop('invoices', []) or []
                product_names: set = set()
                for invoice in invoices:
                    for ip in invoice.get('invoice_products', []) or []:
                        product = ip.get('products')
                        if product and product.get('name'):
                            product_names.add(product['name'])
                customer['products'] = sorted(product_names)

            total_pages = math.ceil(total / page_size) if total > 0 else 1

            logger.info(f"✅ {len(customers)} clientes obtenidos (página {page}/{total_pages})")
            return {
                'success': True,
                'data': customers,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
            }

        except Exception as e:
            logger.error(f"❌ Error obteniendo clientes: {str(e)}")
            return {'success': False, 'error': str(e)}

    def update_customer_reniec_data(self, dni: str, reniec_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza los datos de RENIEC de un cliente existente o crea uno nuevo.
        
        Args:
            dni: DNI del cliente
            reniec_data: Datos completos de la respuesta de RENIEC
            
        Returns:
            Dict con success, data o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            customer_update = {
                'dni': dni.strip(),
                'name': reniec_data.get('full_name', ''),
                'first_name': reniec_data.get('first_name', ''),
                'first_last_name': reniec_data.get('first_last_name', ''),
                'second_last_name': reniec_data.get('second_last_name', '')
            }
            
            # Intentar actualizar primero
            response = self.client.table('customers').update(
                customer_update
            ).eq('dni', dni.strip()).execute()
            
            # Si no hay datos, insertar (upsert)
            if not response.data:
                # No existe, crear nuevo sin phone (será NULL)
                response = self.client.table('customers').insert(customer_update).execute()
            
            if not response.data:
                return {'success': False, 'error': 'No se pudo actualizar/crear el cliente'}
            
            customer = response.data[0]  # type: ignore
            assert isinstance(customer, dict)
            logger.info(f"✅ Datos de RENIEC actualizados para DNI: {dni}")
            return {'success': True, 'data': customer}
            
        except Exception as e:
            logger.error(f"❌ Error actualizando datos de RENIEC: {str(e)}")
            return {'success': False, 'error': str(e)}

