import re
from typing import Any


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

