import re
from typing import Any, Dict, Optional


def clean_apple_watch_model(name: Optional[str]) -> Optional[str]:
    """
    Elimina tamaños de Apple Watch (41/42/44/45/46/49MM) del nombre para guardar limpio.
    
    Args:
        name: Nombre del modelo que puede contener tamaños MM
        
    Returns:
        Nombre limpio sin tamaños MM o None si el input es None/inválido
        
    Examples:
        >>> clean_apple_watch_model("APPLE WATCH SERIES 11 49MM GPS")
        "APPLE WATCH SERIES 11 GPS"
        >>> clean_apple_watch_model("APPLE WATCH ULTRA 2 49MM")
        "APPLE WATCH ULTRA 2"
    """
    if not name or not isinstance(name, str):
        return name
    cleaned = re.sub(r'\b(41|42|44|45|46|49)\s*MM\b', '', name, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned or name.strip()


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
    Mejorado para extraer MÚLTIPLES capacidades (RAM y almacenamiento en MacBooks)
    
    Ejemplo MacBook:
        "MacBook Air (13-inch M4 2025) MBA 13 SKY BLUE 8C GPU 16GB 256GB"
        -> {'brand': 'MACBOOK', 'model': 'AIR (13-INCH M4 2025)', 'color': 'BLUE',
            'capacity': '256GB', 'ram': '16GB', ...}
    
    Ejemplo iPhone:
        "IPHONE 17 PRO MAX SILVER 512GB-USA"
        -> {'brand': 'IPHONE', 'model': '17 PRO MAX', 'color': 'SILVER',
            'capacity': '512GB', 'ram': None, ...}
    """
    
    result: Dict[str, Optional[str]] = {
        'brand': None,
        'model': None,
        'color': None,
        'capacity': None,
        'ram': None,
        'country': None,
        'full_model': None
    }
    
    if not model_desc:
        return result
    
    # Limpiar el string
    desc = model_desc.strip().upper()
    original_desc = desc  # Guardar copia para encontrar capacidades
    
    # 0. ACCESORIOS: Detectar accesorios ANTES de marcas para evitar confusión
    # Ejemplo: "IPAD MAGIC KEYBOARD 13 BLACK-USA" -> brand: KEYBOARD, model: MAGIC KEYBOARD 13
    accessories = {
        'MAGIC KEYBOARD': 'KEYBOARD',
        'SMART KEYBOARD': 'KEYBOARD',
        'KEYBOARD FOLIO': 'KEYBOARD',
        'SMART FOLIO': 'FOLIO',
        'MAGSAFE CHARGER': 'CHARGER',
        'MAGSAFE BATTERY': 'BATTERY PACK',
        'AIRTAG': 'AIRTAG',
    }
    
    detected_accessory = None
    for accessory_pattern, accessory_brand in accessories.items():
        if accessory_pattern in desc:
            detected_accessory = accessory_brand
            # Remover prefijo de producto (IPAD, APPLE, etc.) si existe al inicio
            prefixes_to_remove = ['IPAD ', 'APPLE ', 'IPHONE ', 'MACBOOK ']
            for prefix in prefixes_to_remove:
                if desc.startswith(prefix):
                    desc = desc[len(prefix):].strip()
                    break
            result['brand'] = detected_accessory
            break
    
    # 1. MARCA: Detectar si empieza con IPHONE, APPLE TV, SAMSUNG, etc (solo si no es accesorio)
    if not detected_accessory:
        brands = [
            'APPLE TV', 'APPLE WATCH', 'IPHONE', 'IPAD', 'MACBOOK', 'AIRPODS','APPLE PENCIL'
        ]
        brands.sort(key=len, reverse=True)
        
        for brand in brands:
            if desc.startswith(brand):
                result['brand'] = brand
                desc = desc[len(brand):].strip()
                break
    
    # 2. MÚLTIPLES CAPACIDADES: Buscar TODAS las capacidades (GB/TB/MB)
    capacities = re.findall(r'\b(\d+(?:GB|TB|MB))\b', original_desc, re.IGNORECASE)
    capacities = [c.upper() for c in capacities]
    
    if len(capacities) >= 2 and result['brand'] == 'MACBOOK':
        # MacBook: ordenar y asignar RAM (menor) y almacenamiento (mayor)
        def capacity_to_mb(cap_str: str) -> int:
            match = re.match(r'(\d+)(GB|TB)', cap_str)
            if match:
                value = int(match.group(1))
                unit = match.group(2)
                return value * 1024 if unit == 'TB' else value
            return 0
        
        sorted_caps = sorted(set(capacities), key=capacity_to_mb)
        result['ram'] = sorted_caps[0]  # Menor = RAM
        result['capacity'] = sorted_caps[-1]  # Mayor = almacenamiento
    elif capacities:
        # iPhone, iPad, etc: una sola capacidad
        result['capacity'] = capacities[-1]
    
    # Remover todas las capacidades encontradas del string
    desc_temp = original_desc
    for cap in capacities:
        desc_temp = desc_temp.replace(cap, '').strip()

    # Apple Watch: extraer tamaño (41/42/44/45/46/49mm) como capacidad y removerlo del modelo
    if result['brand'] == 'APPLE WATCH':
        size_match = re.search(r'\b(41|42|44|45|46|49)\s*(?:MM)?\b', original_desc, re.IGNORECASE)
        if size_match:
            size_value = f"{size_match.group(1).upper()}MM"
            result['capacity'] = size_value
            # Quitar cualquier referencia al tamaño para que no quede en el modelo
            desc_temp = re.sub(r'\b(41|42|44|45|46|49)\s*(?:MM)?\b', '', desc_temp, flags=re.IGNORECASE)
            desc_temp = re.sub(r'\s+', ' ', desc_temp).strip()

    desc = desc_temp
    
    # 3. PAÍS: Buscar después de guión o al final (ej: -USA, -CHINA)
    country_match = re.search(r'[-/]([A-Z]{2,}(?:\s+[A-Z]+)?)$', desc)
    if country_match:
        result['country'] = country_match.group(1).strip()
        # Remover país del string
        desc = desc[:country_match.start()].strip()
    
    # 4. COLOR: Buscar colores comunes Y SIGLAS DE COLORES (especialmente para MacBooks)
    # Mapeo de siglas a colores (principalmente para MacBooks)
    color_abbreviations = {
        'SG': 'SPACE GRAY',
        'RG': 'ROSE GOLD',
        'JB': 'JET BLACK',
        'MB': 'MIDNIGHT BLACK',
        'SL': 'SILVER',
        'GD': 'GOLD',
        'BK': 'BLACK',
        'WH': 'WHITE',
        'MN': 'MIDNIGHT',
        'ST': 'STARLIGHT',
        'AB': 'ALPINE BLUE',
        'DB': 'DEEP BLUE',
        'SPB': 'SPACE BLACK',
        'NT': 'NATURAL',
        'SLV': 'SILVER',
        'SLVR': 'SILVER',
        'SBLK': 'SPACE BLACK',
        'SB': 'SPACE BLACK',
    }
    
    colors = [
        'BLACK', 'WHITE', 'SILVER', 'GOLD', 'ROSE GOLD', 'SPACE GRAY', 'SPACE GREY',
        'MIDNIGHT', 'STARLIGHT', 'DEEP BLUE', 'RED', 'GREEN', 'YELLOW', 'PURPLE', 'PINK',
        'CORANGE', 'GRAPHITE', 'SIERRA BLUE', 'ALPINE GREEN', 'DEEP PURPLE','SAGE','DBLUE',
        'TITANIUM', 'NATURAL TITANIUM', 'BLUE TITANIUM', 'WHITE TITANIUM', 'BLACK TITANIUM','BLU',
        'SKY BLUE', 'SPACE BLACK', 'MIDNIGHT BLACK', 'ALPINE BLUE', 'MIST BLUE','LAVENDER', 'BLUE',
    ]
    
    # Ordenar por longitud descendente para los más específicos primero
    colors.sort(key=len, reverse=True)
    
    # Primero intentar colores completos
    for color in colors:
        # Buscar el color al final o antes de otros tokens
        if color in desc:
            result['color'] = color
            # Remover color del string
            desc = desc.replace(color, '').strip()
            break
    
    # Si no encontró color completo, buscar siglas de colores (ej: SB para Space Black)
    if not result['color']:
        for abbr, full_color in color_abbreviations.items():
            # Buscar la sigla como palabra independiente o seguida de números/caracteres
            # Patrón: la sigla seguida de /número o espacio o fin de string
            pattern = rf'\b{re.escape(abbr)}(?=[\s/\d]|$)'
            if re.search(pattern, desc):
                result['color'] = full_color
                # Remover la sigla del string
                desc = re.sub(pattern, '', desc).strip()
                break
    
    # 5. MODELO: Lo que queda es el modelo (sin marca, color, capacidades, país)
    desc = re.sub(r'\s+', ' ', desc).strip()
    
    # Remover menciones adicionales de la marca dentro del modelo para evitar duplicación
    if result['brand'] and desc:
        # Remover todas las ocurrencias de la marca (case insensitive)
        desc = re.sub(r'\b' + re.escape(result['brand']) + r'\b', '', desc, flags=re.IGNORECASE).strip()
        desc = re.sub(r'\s+', ' ', desc).strip()
    
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

