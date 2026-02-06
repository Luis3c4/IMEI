"""
Servicio Supabase - Facade para Repositorios Modulares
=======================================================
Este servicio actúa como facade para los repositorios modulares de Supabase.

Uso:
    from app.services.supabase_service import supabase_service
    
    # Productos
    result = supabase_service.products.save_device_query(...)
    products = supabase_service.products.get_products_with_variants()
    
    # Clientes
    customer = supabase_service.customers.get_or_create_customer(...)
    
    # Dispositivos
    device = supabase_service.devices.get_device(imei)

Base de datos PostgreSQL con API REST/GraphQL
"""

import logging
from typing import Dict, Any, Optional

from .supabase import (
    DeviceRepository,
    ProductRepository,
    CustomerRepository,
    InvoiceRepository
)

logger = logging.getLogger(__name__)


class SupabaseService:
    """
    Facade para repositorios modulares de Supabase.
    Proporciona acceso a los repositorios especializados por dominio:
    - devices: DeviceRepository
    - products: ProductRepository  
    - customers: CustomerRepository
    - invoices: InvoiceRepository
    """
    
    def __init__(self):
        """
        Inicializa el facade con instancias de los repositorios.
        Los repositorios comparten un cliente Singleton para eficiencia.
        """
        # Repositorios públicos
        self.devices = DeviceRepository()
        self.products = ProductRepository()
        self.customers = CustomerRepository()
        self.invoices = InvoiceRepository()
        
        logger.info("✅ SupabaseService inicializado con repositorios modulares")
    
    def is_connected(self) -> bool:
        """
        Verifica si está conectado a Supabase.
        Delega al repositorio base.
        
        Returns:
            True si hay conexión activa, False en caso contrario
        """
        return self.devices.is_connected()


# Instancia global del servicio facade
supabase_service = SupabaseService()
