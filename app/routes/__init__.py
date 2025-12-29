"""
Routes Package - Rutas de la aplicación
Importa y registra todos los blueprints de FastAPI
"""

from . import health, devices, sheets, invoice_routes

__all__ = ['health', 'devices', 'sheets', 'invoice_routes']

