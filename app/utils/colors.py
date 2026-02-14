"""
Mapeo de nombres de colores Apple a códigos hexadecimales
Para visualización de badges de color en el frontend
"""

from typing import Dict, Optional


# Mapeo de colores Apple con sus códigos hexadecimales correspondientes
COLOR_HEX_MAP: Dict[str, str] = {
    # Colores básicos
    'BLACK': '#000000',
    'WHITE': '#FFFFFF',
    'SILVER': '#C0C0C0',
    'GOLD': '#FFD700',
    'ROSE GOLD': '#E0BFB8',
    
    # Colores Space
    'SPACE GRAY': '#747678',
    'SPACE GREY': '#747678',
    'SPACE BLACK': '#1C1C1E',
    
    # Colores iPhone modernos
    'MIDNIGHT': '#1D1D1F',
    'MIDNIGHT BLACK': '#1D1D1F',
    'STARLIGHT': '#F9F6EF',
    'DEEP BLUE': '#1F456E',
    'RED': '#C1292E',
    'GREEN': '#3F5F4D',
    'YELLOW': '#FFD700',
    'PURPLE': '#6E3B6E',
    'PINK': '#FCE4E4',
    'CORANGE': '#FF6B35',
    
    # Colores especiales
    'GRAPHITE': '#41424C',
    'SIERRA BLUE': '#9DB5BB',
    'ALPINE GREEN': '#4F625A',
    'DEEP PURPLE': '#594F63',
    'SAGE': '#B5B89A',
    'DBLUE': '#1F456E',
    
    # Colores Titanium (iPhone 15 Pro)
    'TITANIUM': '#B8B8B8',
    'NATURAL TITANIUM': '#B8B8B8',
    'BLUE TITANIUM': '#5E7A9B',
    'WHITE TITANIUM': '#E8E8E8',
    'BLACK TITANIUM': '#3D3D3D',
    
    # Colores adicionales
    'SKY BLUE': '#87CEEB',
    'ALPINE BLUE': '#6B8E9F',
    'MIST BLUE': '#C5D7E0',
    'LAVENDER': '#E6D7FF',
    'BLUE': '#0071E3',
    
    # Colores MacBook
    'JET BLACK': '#0A0A0A',
}


def get_color_hex(color_name: Optional[str]) -> str:
    """
    Obtiene el código hexadecimal para un nombre de color.
    
    Args:
        color_name: Nombre del color en mayúsculas (ej: 'SILVER', 'SPACE BLACK')
        
    Returns:
        Código hexadecimal del color. Si no se encuentra, retorna gris por defecto.
        
    Examples:
        >>> get_color_hex('SILVER')
        '#C0C0C0'
        >>> get_color_hex('SPACE BLACK')
        '#1C1C1E'
        >>> get_color_hex('UNKNOWN_COLOR')
        '#808080'
        >>> get_color_hex(None)
        '#808080'
    """
    if not color_name:
        return '#808080'  # Gris por defecto
    
    color_upper = color_name.strip().upper()
    return COLOR_HEX_MAP.get(color_upper, '#808080')


def get_color_info(color_name: Optional[str]) -> Dict[str, str]:
    """
    Obtiene información completa del color (nombre y hex).
    
    Args:
        color_name: Nombre del color
        
    Returns:
        Dict con 'name' y 'hex'
        
    Examples:
        >>> get_color_info('SILVER')
        {'name': 'SILVER', 'hex': '#C0C0C0'}
        >>> get_color_info(None)
        {'name': 'UNKNOWN', 'hex': '#808080'}
    """
    if not color_name:
        return {'name': 'UNKNOWN', 'hex': '#808080'}
    
    color_clean = color_name.strip()
    return {
        'name': color_clean,
        'hex': get_color_hex(color_clean)
    }


def get_all_colors() -> Dict[str, str]:
    """
    Retorna todos los colores disponibles con sus códigos hex.
    
    Returns:
        Diccionario completo de colores
    """
    return COLOR_HEX_MAP.copy()
