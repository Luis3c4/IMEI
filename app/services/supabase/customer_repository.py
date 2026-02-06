"""
CustomerRepository - Gestión de clientes
Maneja la tabla: customers
"""

import logging
from typing import Dict, Any
from .base import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class CustomerRepository(BaseSupabaseRepository):
    """Repositorio para operaciones relacionadas con clientes"""
    
    def create_customer(self, name: str, dni: str, 
                       phone:str) -> Dict[str, Any]:
        """
        Crea un nuevo cliente en la base de datos.
        
        Args:
            name: Nombre completo del cliente (requerido)
            dni: DNI del cliente (requerido - identificador único)
            phone: Teléfono del cliente (requerido)
            
        Returns:
            Dict con success, data o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            customer_data = {
                'name': name.strip(),
                'dni': dni.strip(),
                'phone': phone.strip()
            }
            
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
                               phone:str) -> Dict[str, Any]:
        """
        Busca un cliente existente por DNI, o crea uno nuevo si no existe.
        
        Args:
            name: Nombre completo del cliente
            dni: DNI del cliente (requerido - identificador único)
            phone: Teléfono (requerido - debe ser un string no vacío)
            
        Returns:
            Dict con success, data (cliente existente o nuevo), is_new (bool)
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            # Buscar cliente existente por DNI (identificador único)
            dni_search = self.get_customer_by_dni(dni)
            
            if dni_search['success']:
                logger.info(f"✅ Cliente encontrado por DNI: {dni}")
                return {
                    'success': True, 
                    'data': dni_search['data'],
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
