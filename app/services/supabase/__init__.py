"""
Módulo de repositorios Supabase
Arquitectura modular basada en dominios con cliente Singleton compartido

Uso Directo (Recomendado para nuevo código):
    from app.services.supabase import ProductRepository
    product_repo = ProductRepository()
    result = product_repo.save_device_query(...)

Uso a través del Facade (Compatible con código legacy):
    from app.services.supabase_service import supabase_service
    result = supabase_service.products.save_device_query(...)
"""

from .base import BaseSupabaseRepository
from .device_repository import DeviceRepository
from .product_repository import ProductRepository
from .customer_repository import CustomerRepository

__all__ = [
    'BaseSupabaseRepository',
    'DeviceRepository',
    'ProductRepository',
    'CustomerRepository',
]
