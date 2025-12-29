"""
IMEI API Application Package
FastAPI Application Factory
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app(config_name='default'):
    """
    Crea y configura la aplicación FastAPI
    
    Args:
        config_name: Nombre de la configuración a usar (development, production, testing)
        
    Returns:
        FastAPI: Aplicación configurada
    """
    
    app = FastAPI(
        title="IMEI API",
        description="Sistema de consulta de información de dispositivos por IMEI",
        version="2.0.0"
    )
    
    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app
