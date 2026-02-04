"""
Servicio Supabase - Facade Híbrido
==================================
Este servicio actúa como facade para los repositorios modulares de Supabase.

Uso Moderno (Recomendado):
    from app.services.supabase_service import supabase_service
    result = supabase_service.products.save_device_query(...)
    customer = supabase_service.customers.get_or_create_customer(...)

Uso Legacy (Retrocompatibilidad):
    result = supabase_service.save_device_query(...)  # Delega a products
    customer = supabase_service.get_or_create_customer(...)  # Delega a customers

Base de datos PostgreSQL con API REST/GraphQL
"""

import logging
import warnings
from typing import Dict, Any, Optional

from .supabase import (
    DeviceRepository,
    ProductRepository,
    CustomerRepository
)

logger = logging.getLogger(__name__)


class SupabaseService:
    """
    Facade híbrido para repositorios de Supabase.
    Proporciona acceso tanto moderno (vía repositorios) como legacy (métodos directos).
    """
    
    def __init__(self):
        """
        Inicializa el facade con instancias de los repositorios.
        Los repositorios comparten un cliente Singleton para eficiencia.
        """
        # Repositorios públicos (uso moderno)
        self.devices = DeviceRepository()
        self.products = ProductRepository()
        self.customers = CustomerRepository()
        
        logger.info("✅ SupabaseService inicializado con repositorios modulares")
    
    def is_connected(self) -> bool:
        """
        Verifica si está conectado a Supabase.
        Delega al repositorio base.
        
        Returns:
            True si hay conexión activa, False en caso contrario
        """
        return self.devices.is_connected()
    
    # ==================== MÉTODOS LEGACY (DEVICES) ====================
    # ⚠️  Deprecated: Usar supabase_service.devices.* en su lugar
    
    def insert_device(self, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [LEGACY] Inserta un nuevo dispositivo en la BD.
        ⚠️  Deprecated: Usar supabase_service.devices.insert_device()
        """
        warnings.warn(
            "insert_device() está deprecado. Usa supabase_service.devices.insert_device()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.devices.insert_device(device_data)
    
    def get_device(self, imei: str) -> Dict[str, Any]:
        """
        [LEGACY] Obtiene un dispositivo por IMEI.
        ⚠️  Deprecated: Usar supabase_service.devices.get_device()
        """
        warnings.warn(
            "get_device() está deprecado. Usa supabase_service.devices.get_device()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.devices.get_device(imei)
    
    def update_device(self, imei: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [LEGACY] Actualiza un dispositivo.
        ⚠️  Deprecated: Usar supabase_service.devices.update_device()
        """
        warnings.warn(
            "update_device() está deprecado. Usa supabase_service.devices.update_device()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.devices.update_device(imei, device_data)
    
    def list_devices(self, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """
        [LEGACY] Lista todos los dispositivos.
        ⚠️  Deprecated: Usar supabase_service.devices.list_devices()
        """
        warnings.warn(
            "list_devices() está deprecado. Usa supabase_service.devices.list_devices()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.devices.list_devices(limit, offset)
    
    def insert_history(self, history_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        [LEGACY] Inserta un registro de consulta en el historial.
        ⚠️  Deprecated: Usar supabase_service.devices.insert_history()
        """
        warnings.warn(
            "insert_history() está deprecado. Usa supabase_service.devices.insert_history()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.devices.insert_history(history_data)
    
    def get_device_history(self, imei: str, limit: int = 50) -> Dict[str, Any]:
        """
        [LEGACY] Obtiene el historial de consultas de un dispositivo.
        ⚠️  Deprecated: Usar supabase_service.devices.get_device_history()
        """
        warnings.warn(
            "get_device_history() está deprecado. Usa supabase_service.devices.get_device_history()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.devices.get_device_history(imei, limit)
    
    # ==================== MÉTODOS LEGACY (PRODUCTS) ====================
    # ⚠️  Deprecated: Usar supabase_service.products.* en su lugar
    
    def get_products_with_variants(self) -> Dict[str, Any]:
        """
        [LEGACY] Obtiene todos los productos con sus variantes y sus items.
        ⚠️  Deprecated: Usar supabase_service.products.get_products_with_variants()
        """
        warnings.warn(
            "get_products_with_variants() está deprecado. Usa supabase_service.products.get_products_with_variants()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.products.get_products_with_variants()
    
    def save_device_query(self, device_info: Dict[str, Any], metadata: Dict[str, Any], parsed_model: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        [LEGACY] Guarda un dispositivo consultado con toda su información relacionada.
        ⚠️  CRÍTICO: Este método maneja productos, variantes e items.
        ⚠️  Deprecated: Usar supabase_service.products.save_device_query()
        """
        warnings.warn(
            "save_device_query() está deprecado. Usa supabase_service.products.save_device_query()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.products.save_device_query(device_info, metadata, parsed_model)
    
    def update_product_item_status(self, item_id: int, new_status: str) -> Dict[str, Any]:
        """
        [LEGACY] Actualiza el status de un product_item.
        ⚠️  Deprecated: Usar supabase_service.products.update_product_item_status()
        """
        warnings.warn(
            "update_product_item_status() está deprecado. Usa supabase_service.products.update_product_item_status()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.products.update_product_item_status(item_id, new_status)
    
    # ==================== MÉTODOS LEGACY (CUSTOMERS) ====================
    # ⚠️  Deprecated: Usar supabase_service.customers.* en su lugar
    
    def create_customer(self, name: str, dni: str, phone: str) -> Dict[str, Any]:
        """
        [LEGACY] Crea un nuevo cliente en la base de datos.
        ⚠️  Deprecated: Usar supabase_service.customers.create_customer()
        """
        warnings.warn(
            "create_customer() está deprecado. Usa supabase_service.customers.create_customer()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.customers.create_customer(name, dni, phone)
    
    def get_customer_by_dni(self, dni: str) -> Dict[str, Any]:
        """
        [LEGACY] Busca un cliente por su DNI.
        ⚠️  Deprecated: Usar supabase_service.customers.get_customer_by_dni()
        """
        warnings.warn(
            "get_customer_by_dni() está deprecado. Usa supabase_service.customers.get_customer_by_dni()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.customers.get_customer_by_dni(dni)
    
    def get_customer_by_number(self, customer_number: str) -> Dict[str, Any]:
        """
        [LEGACY] Busca clientes por customer_number.
        ⚠️  Deprecated: Usar supabase_service.customers.get_customer_by_number()
        """
        warnings.warn(
            "get_customer_by_number() está deprecado. Usa supabase_service.customers.get_customer_by_number()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.customers.get_customer_by_number(customer_number)
    
    def get_or_create_customer(self, name: str, dni: str, phone: str) -> Dict[str, Any]:
        """
        [LEGACY] Busca un cliente existente por DNI, o crea uno nuevo si no existe.
        ⚠️  Deprecated: Usar supabase_service.customers.get_or_create_customer()
        """
        warnings.warn(
            "get_or_create_customer() está deprecado. Usa supabase_service.customers.get_or_create_customer()",
            DeprecationWarning,
            stacklevel=2
        )
        return self.customers.get_or_create_customer(name, dni, phone)


# Instancia global del servicio (Singleton facade)
supabase_service = SupabaseService()
