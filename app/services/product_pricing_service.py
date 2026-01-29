"""
Servicio para determinar precios de productos Apple basados en el modelo y capacidad

Este servicio utiliza la tabla de precios definida en app/config/pricing.py
y proporciona métodos para buscar precios basándose en modelos parseados.
"""

import logging
import re
from typing import Dict, Optional, Any

from ..config.pricing_pnumbers import APPLE_PRICING_USD

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
                         Debe contener 'full_model' y opcionalmente 'capacity' y 'ram'
        
        Returns:
            Precio del producto en USD o None si no se encuentra
            
        Examples:
            >>> service.get_product_price({'full_model': 'IPHONE 17 PRO', 'capacity': '512GB'})
            1399.0
            >>> service.get_product_price({'full_model': 'MACBOOK PRO (14-INCH M5)', 'capacity': '512GB', 'ram': '16GB'})
            1799.0
        """
        full_model = parsed_model.get('full_model')
        capacity = parsed_model.get('capacity')
        ram = parsed_model.get('ram')
        
        if not full_model:
            logger.warning("⚠️  No se proporcionó 'full_model' en parsed_model")
            return None
        
        # Normalizar el modelo
        model_normalized = full_model.upper().strip()
        
        # Manejo especial para Apple Watch: extraer tamaño del modelo
        capacity = self._extract_capacity_from_model(model_normalized, capacity)
        
        # Combinar RAM y capacidad si ambos existen (para MacBooks)
        combined_capacity = self._combine_capacity_and_ram(capacity, ram)
        
        # Buscar precio en la tabla
        price = self._find_price_in_table(model_normalized, combined_capacity)
        
        return price
    
    def _combine_capacity_and_ram(self, capacity: Optional[str], ram: Optional[str]) -> Optional[str]:
        """
        Combina RAM y capacidad en un solo string para búsqueda de precios
        
        Args:
            capacity: Capacidad de almacenamiento (ej: "512GB")
            ram: Memoria RAM (ej: "16GB")
            
        Returns:
            String combinado (ej: "16GB/512GB") o solo capacidad si no hay RAM
        """
        if ram and capacity:
            return f"{ram}/{capacity}"
        return capacity
    
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
        4. Coincidencia parcial (modelo empieza con clave o contiene clave)
        """
        # Estrategia 1: Coincidencia exacta
        if model in self.pricing_table:
            price = self._get_price_from_table(model, capacity, self.pricing_table[model])
            if price:
                return price
        
        # Estrategia 2: Coincidencia parcial (búsqueda mejorada)
        # Ordenar por longitud descendente para priorizar matches más específicos
        sorted_keys = sorted(self.pricing_table.keys(), key=len, reverse=True)
        
        for model_key in sorted_keys:
            # Buscar si model_key está contenido EN model (importante para full_model con basura)
            # O si model comienza con model_key (fallback para otros casos)
            if model_key in model or model.startswith(model_key):
                price_table = self.pricing_table[model_key]
                price = self._get_price_from_table(model_key, capacity, price_table)
                if price:
                    logger.info(f"💰 Precio encontrado para {model_key} (búsqueda en: {model})")
                    return price
        
        logger.warning(f"⚠️  No se encontró precio para: {model} {capacity or 'no capacity'}")
        return None
    
    def _get_price_from_table(
        self, 
        model: str, 
        capacity: Optional[str], 
        price_table: Dict[str, float]
    ) -> Optional[float]:
        """
        Obtiene el precio de una tabla de precios específica
        
        Estrategia de búsqueda para capacidad:
        1. Capacidad exacta (ejemplo: "16GB/512GB" o "512GB")
        2. Para MacBooks con RAM/Almacenamiento, extrae solo almacenamiento como fallback
        3. Precio DEFAULT
        4. Si solo hay una opción, usar esa
        
        Args:
            model: Nombre del modelo
            capacity: Capacidad buscada (puede ser "16GB/512GB" o "512GB")
            price_table: Diccionario de capacidades y precios
            
        Returns:
            Precio encontrado o None
        """
        if not capacity:
            # Sin capacidad especificada, usar DEFAULT
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
        
        capacity_normalized = capacity.upper()
        
        # Estrategia 1: Buscar por capacidad exacta (ejemplo: "16GB/512GB")
        if capacity_normalized in price_table:
            price = price_table[capacity_normalized]
            logger.info(f"💰 Precio encontrado: {model} {capacity_normalized} = ${price}")
            return price
        
        # Estrategia 2: Para capacidades combinadas (RAM/Almacenamiento), 
        # intentar fallback a solo almacenamiento
        if '/' in capacity_normalized:
            parts = capacity_normalized.split('/')
            storage_only = parts[-1]  # Última parte es almacenamiento
            
            if storage_only in price_table:
                price = price_table[storage_only]
                logger.info(f"💰 Precio fallback (solo almacenamiento): {model} {storage_only} = ${price}")
                return price
        
        # Estrategia 3: Buscar precio DEFAULT
        if 'DEFAULT' in price_table:
            price = price_table['DEFAULT']
            logger.info(f"💰 Precio DEFAULT: {model} = ${price}")
            return price
        
        # Estrategia 4: Si solo hay una opción, usar esa
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
