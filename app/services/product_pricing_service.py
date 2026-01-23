"""
Servicio para determinar precios de productos Apple basados en el modelo y capacidad

Este servicio utiliza la tabla de precios definida en app/config/pricing.py
y proporciona métodos para buscar precios basándose en modelos parseados.
"""

import logging
import re
from typing import Dict, Optional, Any

from ..config.pricing import APPLE_PRICING_USD

logger = logging.getLogger(__name__)


class ProductPricingService:
    """
    Servicio para obtener precios de productos Apple
    
    Attributes:
        pricing_table: Tabla de precios importada desde config/pricing.py
    """
    
    def __init__(self):
        """Inicializa el servicio con la tabla de precios"""
        self.pricing_table = APPLE_PRICING_USD
    
    def get_product_price(self, parsed_model: Dict[str, Optional[str]]) -> Optional[float]:
        """
        Obtiene el precio de un producto basándose en el modelo parseado
        
        Args:
            parsed_model: Diccionario con información del modelo parseado.
                         Debe contener 'full_model' y opcionalmente 'capacity'
        
        Returns:
            Precio del producto en USD o None si no se encuentra
            
        Examples:
            >>> service.get_product_price({'full_model': 'IPHONE 17 PRO', 'capacity': '512GB'})
            1399.0
        """
        full_model = parsed_model.get('full_model')
        capacity = parsed_model.get('capacity')
        
        if not full_model:
            logger.warning("⚠️  No se proporcionó 'full_model' en parsed_model")
            return None
        
        # Normalizar el modelo
        model_normalized = full_model.upper().strip()
        
        # Manejo especial para Apple Watch: extraer tamaño del modelo
        capacity = self._extract_capacity_from_model(model_normalized, capacity)
        
        # Buscar precio en la tabla
        price = self._find_price_in_table(model_normalized, capacity)
        
        return price
    
    def _extract_capacity_from_model(self, model: str, capacity: Optional[str]) -> Optional[str]:
        """
        Extrae la capacidad del modelo si es necesario
        
        Para Apple Watch, extrae el tamaño (41MM, 45MM) del nombre del modelo
        """
        if 'APPLE WATCH' in model:
            size_match = re.search(r'\b(\d+MM)\b', model)
            if size_match:
                return size_match.group(1)
        
        return capacity
    
    def _find_price_in_table(self, model: str, capacity: Optional[str]) -> Optional[float]:
        """
        Busca el precio en la tabla de precios
        
        Estrategia de búsqueda:
        1. Coincidencia exacta con capacidad
        2. Precio DEFAULT si existe
        3. Precio único si solo hay una opción
        4. Coincidencia parcial (modelo empieza con clave)
        """
        # Estrategia 1: Coincidencia exacta
        if model in self.pricing_table:
            price = self._get_price_from_table(model, capacity, self.pricing_table[model])
            if price:
                return price
        
        # Estrategia 2: Coincidencia parcial
        for model_key, price_table in self.pricing_table.items():
            if model.startswith(model_key):
                price = self._get_price_from_table(model_key, capacity, price_table)
                if price:
                    logger.info(f"💰 Precio encontrado (coincidencia parcial) para {model_key}")
                    return price
        
        logger.warning(f"⚠️  No se encontró precio para: {model} {capacity or ''}")
        return None
    
    def _get_price_from_table(
        self, 
        model: str, 
        capacity: Optional[str], 
        price_table: Dict[str, float]
    ) -> Optional[float]:
        """
        Obtiene el precio de una tabla de precios específica
        
        Args:
            model: Nombre del modelo
            capacity: Capacidad buscada
            price_table: Diccionario de capacidades y precios
            
        Returns:
            Precio encontrado o None
        """
        # Buscar por capacidad específica
        if capacity:
            capacity_normalized = capacity.upper()
            if capacity_normalized in price_table:
                price = price_table[capacity_normalized]
                logger.info(f"💰 Precio encontrado: {model} {capacity_normalized} = ${price}")
                return price
        
        # Buscar precio DEFAULT
        if 'DEFAULT' in price_table:
            price = price_table['DEFAULT']
            logger.info(f"💰 Precio DEFAULT: {model} = ${price}")
            return price
        
        # Si solo hay una opción, usar esa
        if len(price_table) == 1:
            price = list(price_table.values())[0]
            logger.info(f"💰 Precio único: {model} = ${price}")
            return price
        
        return None
    
    def get_price_info(self, parsed_model: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        Obtiene información completa de precio del producto
        
        Args:
            parsed_model: Diccionario con información del modelo parseado
            
        Returns:
            Diccionario con información del precio:
            {
                'product_price': float | None,
                'currency': str,
                'price_found': bool,
                'message': str
            }
        """
        product_price = self.get_product_price(parsed_model)
        
        return {
            'product_price': product_price,
            'currency': 'USD',
            'price_found': product_price is not None,
            'message': 'Precio encontrado' if product_price else 'Precio no disponible para este modelo'
        }
    
    def get_available_models(self) -> list[str]:
        """Retorna lista de todos los modelos con precios disponibles"""
        return list(self.pricing_table.keys())
    
    def get_model_variants(self, model: str) -> list[str]:
        """
        Retorna las variantes (capacidades) disponibles para un modelo
        
        Args:
            model: Nombre del modelo (ej: 'IPHONE 17 PRO')
            
        Returns:
            Lista de capacidades disponibles
        """
        model_upper = model.upper()
        if model_upper in self.pricing_table:
            return list(self.pricing_table[model_upper].keys())
        return []


# ============================================================
# Instancia global del servicio
# ============================================================

product_pricing_service = ProductPricingService()
