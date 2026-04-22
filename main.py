"""
FastAPI Application Entry Point
Main server configuration and startup
"""

import uvicorn
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

# Importar los blueprints
from app.routes import health, devices, invoice_routes, products, reniec, customers, admin, orders, historial_routes

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flag para evitar duplicación al recargar con reloader
_routes_registered = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación
    """
    print("\n" + "="*60)
    print("🚀 IMEI API - FastAPI iniciando...")
    print("="*60)
    
    print("\n✅ Servidor listo para recibir peticiones")
    print("📚 Documentación interactiva: http://localhost:8000/docs")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Servidor apagándose...")


def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI
    
    Returns:
        FastAPI: Aplicación configurada
    """
    
    app = FastAPI(
        title="IMEI API",
        description="Sistema de consulta de información de dispositivos por IMEI",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # ============ CORS CONFIGURATION ============
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://falcontec.vercel.app",  # Frontend producción Vercel
            "http://localhost:5173",          # Vite dev local
            "http://localhost:3000",          # React/Next.js local
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000"
        ],
        allow_credentials=True,
        allow_methods=["*"],              # Permitir todos los métodos
        allow_headers=["*"],              # Permitir todos los headers
    )
    
    # ============ REGISTRAR RUTAS ============
    global _routes_registered
    
    if not _routes_registered:
        _routes_registered = True
        print("\n📋 Registrando rutas...")
        
        app.include_router(
            health.router,
            tags=["health"]
        )
        print("   ✓ Health routes registradas (/health)")
        
        app.include_router(
            devices.router,
            prefix="/api/devices",
            tags=["devices"]
        )
        print("   ✓ Devices routes registradas (/api/devices/*)")
        
        app.include_router(
            invoice_routes.router,
            prefix="/api/invoices",
            tags=["invoices"]
        )
        print("   ✓ Invoice routes registradas (/api/invoices/*)")

        app.include_router(
            historial_routes.router,
            prefix="/api/historial",
            tags=["historial"]
        )
        print("   ✓ Historial routes registradas (/api/historial)")
        
        app.include_router(
            products.router,
            prefix="/api/products",
            tags=["products"]
        )
        print("   ✓ Products routes registradas (/api/products/*)")
        
        app.include_router(
            reniec.router,
            prefix="/api/reniec",
            tags=["reniec"]
        )
        print("   ✓ RENIEC routes registradas (/api/reniec/*)")

        app.include_router(
            customers.router,
            prefix="/api/customers",
            tags=["customers"]
        )
        print("   ✓ Customers routes registradas (/api/customers/*)")

        app.include_router(
            admin.router,
            prefix="/api/admin",
            tags=["admin"]
        )
        print("   ✓ Admin routes registradas (/api/admin/*)")

        app.include_router(
            orders.router,
            prefix="/api/orders",
            tags=["orders"]
        )
        print("   ✓ Orders routes registradas (/api/orders/*)")
    else:
        # Solo registrar sin imprimir en recarga
        app.include_router(health.router, tags=["health"])
        app.include_router(devices.router, prefix="/api/devices", tags=["devices"])
        app.include_router(invoice_routes.router, prefix="/api/invoices", tags=["invoices"])
        app.include_router(products.router, prefix="/api/products", tags=["products"])
        app.include_router(reniec.router, prefix="/api/reniec", tags=["reniec"])
        app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
        app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
        app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
    
    # ============ ROOT ENDPOINT ============
    @app.get("/", tags=["root"])
    async def root():
        """Endpoint raíz de bienvenida"""
        return {
            "message": "IMEI API v2.0.0 - FastAPI",
            "status": "running",
            "docs": "/docs",
            "endpoints": {
                "health": "/health",
                "devices": "/api/devices/*",
                "invoices": "/api/invoices/*",
                "products": "/api/products/*",
                "reniec": "/api/reniec/*",
                "customers": "/api/customers/*"
            }
        }
    
    @app.get("/health", tags=["health"])
    async def quick_health():
        """Health check rápido (alternativo)"""
        return {"status": "ok"}
    
    return app


# Crear instancia de la app
app = create_app()


if __name__ == "__main__":
    # Ejecutar con uvicorn (SOLO PARA DESARROLLO LOCAL)
    # En producción se usa Gunicorn (ver Dockerfile)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Solo para desarrollo
        log_level="info"
    )
