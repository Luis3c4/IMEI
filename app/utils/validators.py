"""
Validadores para datos de entrada (IMEI, Serial Number, etc.)
Centraliza toda la lógica de validación del sistema
"""

import re
from typing import Dict, Any, Tuple

class ValidationError(Exception):
    """Excepción personalizada para errores de validación"""
    pass


class IMEIValidator:
    """Validador para números IMEI"""
    
    @staticmethod
    def is_valid_format(imei: str) -> bool:
        """
        Valida que el IMEI tenga formato correcto (15 dígitos)
        
        Args:
            imei: String con el IMEI a validar
            
        Returns:
            bool: True si es válido, False si no
        """
        if not imei:
            return False
        
        # Limpiar espacios y guiones
        imei_clean = imei.replace(' ', '').replace('-', '')
        
        # Debe tener exactamente 15 dígitos
        return bool(re.match(r'^\d{15}$', imei_clean))
    
    @staticmethod
    def luhn_check(imei: str) -> bool:
        """
        Valida el dígito de control usando el algoritmo de Luhn
        
        Args:
            imei: String con el IMEI (15 dígitos)
            
        Returns:
            bool: True si pasa la validación de Luhn
        """
        imei_clean = imei.replace(' ', '').replace('-', '')
        
        if not re.match(r'^\d{15}$', imei_clean):
            return False
        
        # Algoritmo de Luhn
        digits = [int(d) for d in imei_clean]
        check_digit = digits[-1]
        imei_without_check = digits[:-1]
        
        # Duplicar cada segundo dígito de derecha a izquierda
        for i in range(len(imei_without_check) - 1, -1, -2):
            imei_without_check[i] *= 2
            if imei_without_check[i] > 9:
                imei_without_check[i] -= 9
        
        total = sum(imei_without_check)
        calculated_check = (10 - (total % 10)) % 10
        
        return calculated_check == check_digit
    
    @staticmethod
    def validate(imei: str, check_luhn: bool = True) -> Tuple[bool, str]:
        """
        Validación completa del IMEI
        
        Args:
            imei: String con el IMEI
            check_luhn: Si debe verificar el dígito de control
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not imei:
            return False, "IMEI vacío"
        
        imei_clean = imei.replace(' ', '').replace('-', '')
        
        if not IMEIValidator.is_valid_format(imei):
            return False, "IMEI debe tener exactamente 15 dígitos"
        
        if check_luhn and not IMEIValidator.luhn_check(imei_clean):
            return False, "IMEI no pasa validación de Luhn (dígito de control incorrecto)"
        
        return True, "IMEI válido"


class SerialNumberValidator:
    """Validador para números de serie de Apple"""
    
    # Formatos conocidos de serial numbers de Apple
    FORMATS = {
        'compact': r'^[A-Z0-9]{10}$',  # Formato compacto (10 caracteres)
        'old': r'^[A-Z0-9]{11}$',      # Formato antiguo (11 caracteres)
        'new': r'^[A-Z0-9]{12}$',      # Formato nuevo (12 caracteres)
        'imac': r'^[A-Z0-9]{13}$',     # iMac y algunos Mac (13 caracteres)
    }
    
    @staticmethod
    def is_valid_format(serial: str) -> bool:
        """
        Valida que el serial number tenga un formato válido de Apple
        
        Args:
            serial: String con el serial number
            
        Returns:
            bool: True si coincide con algún formato conocido
        """
        if not serial:
            return False
        
        serial_clean = serial.strip().upper()
        
        # Verificar contra formatos conocidos
        for format_name, pattern in SerialNumberValidator.FORMATS.items():
            if re.match(pattern, serial_clean):
                return True
        
        return False
    
    @staticmethod
    def validate(serial: str) -> Tuple[bool, str]:
        """
        Validación completa del serial number
        
        Args:
            serial: String con el serial number
            
        Returns:
            Tuple[bool, str]: (es_valido, mensaje_error)
        """
        if not serial:
            return False, "Serial number vacío"
        
        serial_clean = serial.strip().upper()
        
        if len(serial_clean) < 8:
            return False, "Serial number demasiado corto (mínimo 8 caracteres)"
        
        if len(serial_clean) > 20:
            return False, "Serial number demasiado largo (máximo 20 caracteres)"
        
        # Validar caracteres alfanuméricos
        if not re.match(r'^[A-Z0-9]+$', serial_clean):
            return False, "Serial number solo debe contener letras y números"
        
        if not SerialNumberValidator.is_valid_format(serial_clean):
            return False, f"Formato de serial number no reconocido (longitud: {len(serial_clean)})"
        
        return True, "Serial number válido"


class DeviceInputValidator:
    """Validador general para inputs de dispositivos (IMEI o Serial)"""
    
    @staticmethod
    def detect_type(input_value: str) -> str:
        """
        Detecta automáticamente si el input es IMEI o Serial Number
        
        Args:
            input_value: String con el input del usuario
            
        Returns:
            str: 'imei', 'serial', o 'unknown'
        """
        if not input_value:
            return 'unknown'
        
        clean_value = input_value.replace(' ', '').replace('-', '').strip()
        
        # Si son 15 dígitos, probablemente es IMEI
        if re.match(r'^\d{15}$', clean_value):
            return 'imei'
        
        # Si tiene letras y números, probablemente es serial
        if re.match(r'^[A-Z0-9]{8,20}$', clean_value.upper()):
            return 'serial'
        
        return 'unknown'
    
    @staticmethod
    def validate(input_value: str, expected_type = None ) -> Dict[str, Any]:
        """
        Valida el input del dispositivo
        
        Args:
            input_value: String con el input del usuario
            expected_type: Tipo esperado ('imei', 'serial', o None para auto-detectar)
            
        Returns:
            Dict con: {
                'valid': bool,
                'type': str,
                'cleaned_value': str,
                'message': str
            }
        """
        if not input_value or not input_value.strip():
            return {
                'valid': False,
                'type': 'unknown',
                'cleaned_value': '',
                'message': 'Input vacío'
            }
        
        cleaned = input_value.replace(' ', '').replace('-', '').strip().upper()
        
        # Auto-detectar tipo si no se especifica
        if not expected_type:
            detected_type = DeviceInputValidator.detect_type(input_value)
        else:
            detected_type = expected_type
        
        # Validar según el tipo
        if detected_type == 'imei':
            is_valid, message = IMEIValidator.validate(cleaned, check_luhn=False)
            return {
                'valid': is_valid,
                'type': 'imei',
                'cleaned_value': cleaned,
                'message': message
            }
        
        elif detected_type == 'serial':
            is_valid, message = SerialNumberValidator.validate(cleaned)
            return {
                'valid': is_valid,
                'type': 'serial',
                'cleaned_value': cleaned,
                'message': message
            }
        
        else:
            return {
                'valid': False,
                'type': 'unknown',
                'cleaned_value': cleaned,
                'message': 'No se pudo detectar el tipo de input (IMEI o Serial)'
            }


class InventoryValidator:
    """Validadores para operaciones de inventario"""
    
    @staticmethod
    def validate_stock(cantidad: int) -> Tuple[bool, str]:
        """Valida cantidad de stock"""
        if cantidad < 0:
            return False, "La cantidad no puede ser negativa"
        if cantidad > 10000:
            return False, "Cantidad excesiva (máximo 10,000)"
        return True, "Cantidad válida"
    
    @staticmethod
    def validate_precio(precio: float) -> Tuple[bool, str]:
        """Valida precio"""
        if precio < 0:
            return False, "El precio no puede ser negativo"
        if precio > 1000000:
            return False, "Precio excesivo (máximo $1,000,000)"
        return True, "Precio válido"
    
    @staticmethod
    def validate_descuento(descuento: float, precio_venta: float) -> Tuple[bool, str]:
        """Valida que el descuento no exceda el precio de venta"""
        if descuento < 0:
            return False, "El descuento no puede ser negativo"
        if descuento > precio_venta:
            return False, f"El descuento (${descuento}) no puede ser mayor al precio de venta (${precio_venta})"
        return True, "Descuento válido"
    
    @staticmethod
    def validate_venta(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida todos los campos necesarios para una venta
        
        Args:
            data: Dict con los datos de la venta
            
        Returns:
            Dict con: {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str]
            }
        """
        errors = []
        warnings = []
        
        # Validaciones obligatorias
        if not data.get('inventario_id'):
            errors.append("inventario_id es obligatorio")
        
        if not data.get('precio_venta'):
            errors.append("precio_venta es obligatorio")
        else:
            is_valid, msg = InventoryValidator.validate_precio(data['precio_venta'])
            if not is_valid:
                errors.append(msg)
        
        # Validar descuento si existe
        descuento = data.get('descuento', 0)
        if descuento > 0:
            is_valid, msg = InventoryValidator.validate_descuento(
                descuento, 
                data.get('precio_venta', 0)
            )
            if not is_valid:
                errors.append(msg)
        
        # Validar datos del cliente (opcionales pero útiles)
        if not data.get('cliente_nombre'):
            warnings.append("Se recomienda registrar el nombre del cliente")
        
        if not data.get('cliente_telefono') and not data.get('cliente_email'):
            warnings.append("Se recomienda registrar al menos un método de contacto del cliente")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }