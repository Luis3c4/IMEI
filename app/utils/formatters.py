"""
Utilidades para formatear datos para presentación
Incluye formateo de fechas en español, números, monedas, etc.
"""

from datetime import datetime
from typing import Optional


# Mapeo de meses en español
MESES_ESPANOL = {
    1: 'enero',
    2: 'febrero',
    3: 'marzo',
    4: 'abril',
    5: 'mayo',
    6: 'junio',
    7: 'julio',
    8: 'agosto',
    9: 'septiembre',
    10: 'octubre',
    11: 'noviembre',
    12: 'diciembre'
}


def format_date_spanish(date_input: Optional[str | datetime]) -> str:
    """
    Formatea una fecha en español con formato "DD de mes".
    
    Args:
        date_input: Fecha en formato ISO (str), datetime o None
        
    Returns:
        Fecha formateada como "29 de enero" o "Sin actualización" si es None
        
    Examples:
        >>> format_date_spanish('2026-01-29')
        '29 de enero'
        >>> format_date_spanish('2026-12-25T10:30:00')
        '25 de diciembre'
        >>> format_date_spanish(datetime(2026, 2, 14))
        '14 de febrero'
        >>> format_date_spanish(None)
        'Sin actualización'
    """
    if date_input is None:
        return 'Sin actualización'
    
    try:
        # Si es string, parsear a datetime
        if isinstance(date_input, str):
            # Intentar parsear diferentes formatos
            # ISO: 2026-01-29T10:30:00+00:00 o 2026-01-29
            if 'T' in date_input:
                date_obj = datetime.fromisoformat(date_input.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_input, '%Y-%m-%d')
        elif isinstance(date_input, datetime):
            date_obj = date_input
        else:
            return 'Sin actualización'
        
        # Formatear en español
        day = date_obj.day
        month = MESES_ESPANOL.get(date_obj.month, '')
        
        return f"{day} de {month}"
    
    except (ValueError, AttributeError) as e:
        return 'Sin actualización'


def format_date_full_spanish(date_input: Optional[str | datetime]) -> str:
    """
    Formatea una fecha completa en español con formato "DD de mes de YYYY".
    
    Args:
        date_input: Fecha en formato ISO (str), datetime o None
        
    Returns:
        Fecha formateada como "29 de enero de 2026"
        
    Examples:
        >>> format_date_full_spanish('2026-01-29')
        '29 de enero de 2026'
        >>> format_date_full_spanish(None)
        'Sin fecha'
    """
    if date_input is None:
        return 'Sin fecha'
    
    try:
        if isinstance(date_input, str):
            if 'T' in date_input:
                date_obj = datetime.fromisoformat(date_input.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_input, '%Y-%m-%d')
        elif isinstance(date_input, datetime):
            date_obj = date_input
        else:
            return 'Sin fecha'
        
        day = date_obj.day
        month = MESES_ESPANOL.get(date_obj.month, '')
        year = date_obj.year
        
        return f"{day} de {month} de {year}"
    
    except (ValueError, AttributeError):
        return 'Sin fecha'


def format_currency(amount: Optional[float], currency: str = 'USD') -> str:
    """
    Formatea un monto como moneda.
    
    Args:
        amount: Monto a formatear
        currency: Código de moneda (USD, PEN, etc.)
        
    Returns:
        Monto formateado con símbolo de moneda
        
    Examples:
        >>> format_currency(1199.99, 'USD')
        '$1,199.99'
        >>> format_currency(4500.50, 'PEN')
        'S/ 4,500.50'
        >>> format_currency(None)
        '$0.00'
    """
    if amount is None:
        amount = 0.0
    
    symbols = {
        'USD': '$',
        'PEN': 'S/',
        'EUR': '€'
    }
    
    symbol = symbols.get(currency, currency + ' ')
    formatted = f"{amount:,.2f}"
    
    return f"{symbol}{formatted}"


def format_number(number: Optional[int | float]) -> str:
    """
    Formatea un número con separadores de miles.
    
    Args:
        number: Número a formatear
        
    Returns:
        Número formateado con comas
        
    Examples:
        >>> format_number(1000)
        '1,000'
        >>> format_number(1500.50)
        '1,500.50'
    """
    if number is None:
        return '0'
    
    if isinstance(number, float):
        return f"{number:,.2f}"
    
    return f"{number:,}"
