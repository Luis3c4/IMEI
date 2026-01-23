"""
Configuración de precios de productos Apple
Precios en USD - Enero 2026

Estructura:
{
    'MODELO': {
        'CAPACIDAD': precio_float
    }
}

Notas:
- Para productos sin variantes de capacidad, usar 'DEFAULT'
- Para Apple Watch, las capacidades son tamaños (41MM, 45MM, etc.)
- Actualizar estos precios cuando Apple publique nuevos modelos o cambios de precio
"""

from typing import Dict


# ============================================================
# PRECIOS DE PRODUCTOS APPLE (USD - Enero 2026)
# ============================================================

APPLE_PRICING_USD: Dict[str, Dict[str, float]] = {
    # ============================================================
    # iPhone Series
    # ============================================================
    
    # iPhone 17 Pro / Pro Max
    'IPHONE 17 PRO': {
        '128GB': 1099.0,
        '256GB': 1199.0,
        '512GB': 1399.0,
        '1TB': 1599.0,
    },
    'IPHONE 17 PRO MAX': {
        '128GB': 1099.0,
        '256GB': 1199.0,
        '512GB': 1399.0,
        '1TB': 1599.0,
    },
    
    # iPhone 17 Base
    'IPHONE 17': {
        '128GB': 799.0,
        '256GB': 899.0,
        '512GB': 1099.0,
    },
    
    # iPhone 17 Air
    'IPHONE 17 AIR': {
        '128GB': 999.0,
        '256GB': 1099.0,
    },
    
    # ============================================================
    # MacBook Series
    # ============================================================
    
    # MacBook Air M3
    'MACBOOK AIR M3': {
        '256GB': 999.0,
        '512GB': 1299.0,
    },
    
    # MacBook Pro 14" M5
    'MACBOOK PRO 14': {
        '512GB': 1599.0,
        '1TB': 1999.0,
    },
    
    # MacBook Pro 16" M5
    'MACBOOK PRO 16': {
        '512GB': 2499.0,
        '1TB': 2899.0,
    },
    
    # ============================================================
    # Apple Watch Series
    # ============================================================
    
    # Apple Watch Series 11
    'APPLE WATCH SERIES 11': {
        '41MM': 399.0,
        '45MM': 429.0,
    },
    
    # Apple Watch Ultra 3
    'APPLE WATCH ULTRA 3': {
        '49MM': 799.0,
    },
    
    # Apple Watch SE
    'APPLE WATCH SE': {
        '40MM': 249.0,
        '44MM': 279.0,
    },
    
    # ============================================================
    # Apple TV
    # ============================================================
    
    'APPLE TV 4K': {
        '64GB': 129.0,
        '128GB': 149.0,
        'DEFAULT': 129.0,  # Precio base si no se especifica capacidad
    },
    
    # ============================================================
    # iPad Series
    # ============================================================
    
    # iPad Pro M5
    'IPAD PRO': {
        '128GB': 999.0,
        '256GB': 1099.0,
        '512GB': 1299.0,
        '1TB': 1899.0,
    },
    
    # iPad Air M2
    'IPAD AIR': {
        '64GB': 549.0,
        '256GB': 699.0,
    },
    
    # iPad Base (10ª Gen)
    'IPAD': {
        '64GB': 329.0,
        '256GB': 479.0,
    },
    
    # ============================================================
    # AirPods Series
    # ============================================================
    
    'AIRPODS': {
        'DEFAULT': 129.0,
    },
    
    'AIRPODS PRO': {
        'DEFAULT': 249.0,
    },
    
    'AIRPODS MAX': {
        'DEFAULT': 549.0,
    },
}


# ============================================================
# FUNCIONES HELPER
# ============================================================

def get_all_models() -> list[str]:
    """Retorna lista de todos los modelos disponibles"""
    return list(APPLE_PRICING_USD.keys())


def get_model_capacities(model: str) -> list[str]:
    """Retorna las capacidades disponibles para un modelo"""
    model_upper = model.upper()
    if model_upper in APPLE_PRICING_USD:
        return list(APPLE_PRICING_USD[model_upper].keys())
    return []


def get_price_range(model: str) -> tuple[float, float] | None:
    """Retorna el rango de precios (min, max) para un modelo"""
    model_upper = model.upper()
    if model_upper in APPLE_PRICING_USD:
        prices = [p for k, p in APPLE_PRICING_USD[model_upper].items() if k != 'DEFAULT']
        if prices:
            return (min(prices), max(prices))
    return None
