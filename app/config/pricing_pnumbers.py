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
        '256GB': 1099.0,
        '512GB': 1299.0,
        '1TB': 1499.0,
    },
    'IPHONE 17 PRO MAX': {  
        '256GB': 1199.0,
        '512GB': 1399.0,
        '1TB': 1599.0,
        '2TB': 1999.0,
    },
    
    # iPhone 17 Base
    'IPHONE 17': {
        '128GB': 699.0,
        '256GB': 799.0,
        '512GB': 999.0,
    },
    
    # iPhone 17 Air
    'IPHONE 17 AIR': {
        '256GB': 1099.0,
    },
    
    # ============================================================
    # MacBook Series
    # ============================================================
    
    # MacBook Air M4
    'MACBOOK AIR (13-INCH M4': {
        '16GB/256GB': 999.0,
        '16GB/512GB': 1199.0,
        '24GB/512GB': 1399.0,
        # Fallback por capacidad de almacenamiento solo
        '256GB': 999.0,
        '512GB': 1299.0,
        'DEFAULT': 999.0,
    },
    'MACBOOK AIR (15-INCH M4': {
        '16GB/256GB': 1199.0,
        '16GB/512GB': 1399.0,
        '24GB/512GB': 1599.0,
        # Fallback por capacidad de almacenamiento solo
        '256GB': 1199.0,
        '512GB': 1399.0,
        'DEFAULT': 1199.0,
    },
    # MacBook Pro 14" M4 PRO/MAX
    'MACBOOK PRO (14-INCH': {   
        '24GB/512GB': 1999.0,
        '24GB/1TB': 2399.0,
        '36GB/1TB': 2399.0,
        # Fallback por capacidad de almacenamiento solo
        '512GB': 1599.0,
        '1TB': 1999.0,
    },
    
    # MacBook Pro 16" M4 PRO/MAX
    'MACBOOK PRO (16-INCH': {
        '24GB/512GB': 2499.0,
        '48GB/512GB': 2899.0,
        '16GB/1TB': 2899.0,
        # Fallback por capacidad de almacenamiento solo
        '512GB': 2499.0,
        '1TB': 2899.0,
    },

    # MacBook Pro 14" M5
    'MACBOOK PRO (14-INCH M5)': {   
        '16GB/512GB': 1599.0,
        '16GB/1TB': 1799.0,
        '24GB/1TB': 1999.0,
        # Fallback por capacidad de almacenamiento solo
        '512GB': 1599.0,
        '1TB': 1999.0,
    },
    
    # ============================================================
    # Apple Watch Series
    # ============================================================
    
    # Apple Watch Series 11
    'APPLE WATCH SERIES 11': {
        '42MM': 399.0,
        '46MM': 429.0,
    },
    
    # Apple Watch Ultra 3
    'APPLE WATCH ULTRA 3': {
        '49MM': 799.0,
    },
    # Apple Watch Ultra 2
    'APPLE WATCH ULTRA 2': {
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
    'IPAD MINI': {
        '128GB': 499.0,
        '256GB': 599.0,
        '512GB': 799.0,
    },
    # iPad Pro M5
    'IPAD PRO 11-INCH': {
        '256GB': 999.0,
        '512GB': 1199.0,
        '1TB': 1599.0,
        '2TB': 1999.0,
    },
    'IPAD PRO 13-INCH': {
        '256GB': 1299.0,
        '512GB': 1499.0,
        '1TB': 1899.0,
        '2TB': 2299.0,
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

    # ============================================================
    # Magic Keyboard Series
    # ============================================================

    'IPAD MAGIC KEYBOARD': {
        'DEFAULT': 299.0,
    },
    
    # ============================================================
    # Apple Pencil Series
    # ============================================================
    'APPLE PENCIL PRO': {
        'DEFAULT': 129.0,
    },
    # ============================================================
    # Mackook whit ñ
    # ============================================================
    'MACBOOK AIR': {
        'DEFAULT': 1220.0,
    }
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


# ============================================================
# PRODUCT NUMBERS ESTÁTICOS (Para productos sin variantes)
# ============================================================

STATIC_PRODUCT_NUMBERS: Dict[str, str] = {
    # Apple Watch - Todos comparten el mismo Product Number
    'APPLE WATCH SERIES 11': 'MEUX4LW/A',
    'APPLE WATCH SE': 'MX2D3AM/A',
    
    # Apple TV
    'APPLE TV 4K': 'MN893LL/A',

    # Ipad pro
    'IPAD PRO 13-INCH': 'MPF37LL/A',
    'IPAD PRO 11-INCH': 'MRP4RLL/A',
    
    # AirPods
    'AIRPODS': 'MX2D3AM/A',
    'AIRPODS PRO': 'MFHP4LL/A',
    'AIRPODS MAX': 'MX2D3AM/A',

    # Magic Keyboard
    'MAGIC KEYBOARD': 'MWR23LL/A',

    # Apple Pencil
    'APPLE PENCIL PRO': 'MX2D3AM/A',

    # Macbook whit ñ
    'MACBOOK AIR': 'MEE3LUIS/A',
}


def get_static_product_number(product_name: str) -> str | None:
    """
    Obtiene el Product Number estático para productos que no varían
    (Apple Watch, AirPods, Apple TV)
    
    Args:
        product_name: Nombre del producto completo
        
    Returns:
        Product Number estático o None si no aplica
    
    Examples:
        >>> get_static_product_number('APPLE WATCH SERIES 11')
        'MX2D3AM/A'
        >>> get_static_product_number('IPHONE 17 PRO')
        None
    """
    product_upper = product_name.upper()
    
    # Buscar coincidencia exacta primero
    if product_upper in STATIC_PRODUCT_NUMBERS:
        return STATIC_PRODUCT_NUMBERS[product_upper]
    
    # Buscar coincidencia parcial
    for product_key, product_number in STATIC_PRODUCT_NUMBERS.items():
        if product_key in product_upper:
            return product_number
    
    return None
