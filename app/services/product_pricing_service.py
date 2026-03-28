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
        chip = parsed_model.get('chip')
        
        if not full_model:
            logger.warning("⚠️  No se proporcionó 'full_model' en parsed_model")
            return None
        
        # Normalizar el modelo
        model_normalized = full_model.upper().strip()
        
        # Manejo especial para Apple Watch: extraer tamaño del modelo
        capacity = self._extract_capacity_from_model(model_normalized, capacity)
        
        # Combinar RAM, capacidad y chip (para MacBooks)
        combined_capacity = self._combine_capacity_ram_chip(capacity, ram, chip)
        
        # Buscar precio en la tabla
        price = self._find_price_in_table(model_normalized, combined_capacity)
        
        return price
    
    def _combine_capacity_ram_chip(
        self,
        capacity: Optional[str],
        ram: Optional[str],
        chip: Optional[str],
    ) -> Optional[str]:
        """
        Combina RAM, capacidad y chip en un solo string para búsqueda de precios.

        Orden de prioridad (más específico primero):
          - ram/capacity/chip  →  "16GB/512GB/10C CPU / 8C GPU"
          - ram/capacity       →  "16GB/512GB"
          - capacity           →  "512GB"
        """
        if ram and capacity and chip:
            return f"{ram}/{capacity}/{chip}"
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
        
        # Estrategia 1: Buscar por capacidad exacta (ejemplo: "16GB/512GB/10C CPU / 8C GPU")
        if capacity_normalized in price_table:
            price = price_table[capacity_normalized]
            logger.info(f"💰 Precio encontrado: {model} {capacity_normalized} = ${price}")
            return price
        
        # Estrategia 2: Para capacidades combinadas con chip (RAM/Almacenamiento/Chip),
        # intentar fallback a RAM/Almacenamiento sin chip, luego solo almacenamiento.
        parts = capacity_normalized.split('/')
        if len(parts) >= 3:
            # Tiene chip: intentar ram/storage sin chip
            ram_storage = f"{parts[0]}/{parts[1]}"
            if ram_storage in price_table:
                price = price_table[ram_storage]
                logger.info(f"💰 Precio fallback (sin chip): {model} {ram_storage} = ${price}")
                return price
            # Fallback a solo almacenamiento
            storage_only = parts[1]
            if storage_only in price_table:
                price = price_table[storage_only]
                logger.info(f"💰 Precio fallback (solo almacenamiento): {model} {storage_only} = ${price}")
                return price
        elif len(parts) == 2:
            # Tiene ram/storage: intentar solo almacenamiento
            storage_only = parts[-1]
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
