"""
Routes Package - Rutas de la aplicación
Importa y registra todos los blueprints de FastAPI
"""

from . import health, devices, invoice_routes

__all__ = ['health', 'devices', 'invoice_routes']

