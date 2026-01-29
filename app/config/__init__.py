"""
Módulo de configuración de la aplicación
Incluye configuración de la aplicación y precios de productos
"""

from .settings import settings, Settings, DevelopmentConfig, ProductionConfig
from .pricing_pnumbers import (
    APPLE_PRICING_USD,
    get_all_models,
    get_model_capacities,
    get_price_range,
)

__all__ = [
    # Settings
    'settings',
    'Settings',
    'DevelopmentConfig',
    'ProductionConfig',
    # Pricing
    'APPLE_PRICING_USD',
    'get_all_models',
    'get_model_capacities',
    'get_price_range',
]

