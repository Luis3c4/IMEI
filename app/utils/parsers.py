import re
from typing import Any, Dict, Optional


def normalize_keys(obj: Any) -> Any:
    """
    Normaliza recursivamente las claves de diccionarios reemplazando espacios con guiones bajos
    
    Ejemplos:
        'Serial Number' -> 'Serial_Number'
        'iCloud Lock' -> 'iCloud_Lock'
    
    Args:
        obj: Diccionario, lista o valor a normalizar
        
    Returns:
        Objeto con keys normalizadas
    """
    if isinstance(obj, dict):
        normalized = {}
        for key, value in obj.items():
            # Solo operar en keys que son strings
            if isinstance(key, str):
                # Reemplazar espacios múltiples con underscore
                new_key = re.sub(r"\s+", "_", key.strip())
            else:
                new_key = key
            
            # Recursión para valores anidados
            normalized[new_key] = normalize_keys(value)
        return normalized
    
    elif isinstance(obj, list):
        return [normalize_keys(item) for item in obj]
    
    else:
        return obj


def parse_model_description(model_desc: str) -> Dict[str, Optional[str]]:
    """
    Parsea el campo Model_Description para extraer información estructurada
    
    Ejemplo:
        "IPHONE 17 PRO MAX SILVER 512GB-USA"
        
    Returns:
        {
            'brand': 'IPHONE',
            'model': '17 PRO MAX',
            'color': 'SILVER',
            'capacity': '512GB',
            'country': 'USA',
            'full_model': 'IPHONE 17 PRO MAX'
        }
    """
    
    result: Dict[str, Optional[str]] = {
        'brand': None,
        'model': None,
        'color': None,
        'capacity': None,
        'country': None,
        'full_model': None
    }
    
    if not model_desc:
        return result
    
    # Limpiar el string
    desc = model_desc.strip().upper()
    
    # 1. MARCA: Detectar si empieza con IPHONE, APPLE TV, SAMSUNG, etc
    # Ordenar por longitud para matchear primero las más específicas
    brands = [
        'APPLE TV', 'APPLE WATCH', 'IPHONE', 'IPAD', 'MACBOOK', 'AIRPODS'
    ]
    brands.sort(key=len, reverse=True)
    
    for brand in brands:
        if desc.startswith(brand):
            result['brand'] = brand
            desc = desc[len(brand):].strip()
            break
    
    # 2. CAPACIDAD: Buscar patrón como 512GB, 1TB, etc
    capacity_match = re.search(r'\b(\d+(?:GB|TB|MB))\b', desc, re.IGNORECASE)
    if capacity_match:
        result['capacity'] = capacity_match.group(1).upper()
        # Remover capacidad del string
        desc = desc.replace(capacity_match.group(0), '').strip()
    
    # 3. PAÍS: Buscar después de guión o al final (ej: -USA, -CHINA)
    country_match = re.search(r'[-/]([A-Z]{2,}(?:\s+[A-Z]+)?)$', desc)
    if country_match:
        result['country'] = country_match.group(1).strip()
        # Remover país del string
        desc = desc[:country_match.start()].strip()
    
    # 4. COLOR: Buscar colores comunes al final del string
    colors = [
        'BLACK', 'WHITE', 'SILVER', 'GOLD', 'ROSE GOLD', 'SPACE GRAY', 'SPACE GREY',
        'MIDNIGHT', 'STARLIGHT', 'BLUE', 'RED', 'GREEN', 'YELLOW', 'PURPLE', 'PINK',
        'CORANGE', 'GRAPHITE', 'SIERRA BLUE', 'ALPINE GREEN', 'DEEP PURPLE',
        'TITANIUM', 'NATURAL TITANIUM', 'BLUE TITANIUM', 'WHITE TITANIUM', 'BLACK TITANIUM'
    ]
    
    # Ordenar colores por longitud descendente para matchear los más específicos primero
    colors.sort(key=len, reverse=True)
    
    for color in colors:
        # Buscar el color al final o antes de otros tokens
        if color in desc:
            result['color'] = color
            # Remover color del string
            desc = desc.replace(color, '').strip()
            break
    
    # 5. MODELO: Lo que queda es el modelo
    desc = re.sub(r'\s+', ' ', desc).strip()  # Normalizar espacios
    if desc:
        result['model'] = desc
    
    # 6. FULL MODEL: Combinar marca + modelo
    if result['brand'] and result['model']:
        result['full_model'] = f"{result['brand']} {result['model']}"
    elif result['brand']:
        result['full_model'] = result['brand']
    elif result['model']:
        result['full_model'] = result['model']
    
    return result

