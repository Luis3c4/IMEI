"""
InvoiceRepository - Gestión de facturas
Maneja la tabla: invoices
"""

import logging
from typing import Dict, Any
from .base import BaseSupabaseRepository

logger = logging.getLogger(__name__)


class InvoiceRepository(BaseSupabaseRepository):
    """Repositorio para operaciones relacionadas con facturas"""
    
    def create_invoice(self, invoice_number: str, invoice_date: str) -> Dict[str, Any]:
        """
        Crea una nueva factura en la base de datos.
        El customer_number se genera automáticamente en la BD mediante trigger.
        
        Args:
            invoice_number: Número de factura generado por el frontend (ej: "MA85377130")
            invoice_date: Fecha de la factura (ej: "September 04, 2025")
            
        Returns:
            Dict con success, data (incluyendo customer_number generado automáticamente) o error
        """
        if not self.client:
            return {'success': False, 'error': 'Cliente de Supabase no inicializado'}
        
        try:
            invoice_data = {
                'invoice_number': invoice_number.strip(),
                'invoice_date': invoice_date.strip()
                # customer_number se genera automáticamente por trigger
            }
            
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
