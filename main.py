"""
FastAPI Application Entry Point
Main server configuration and startup
"""

import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Importar los blueprints
from app.routes import health, devices, sheets

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación
    """
    print("\n" + "="*60)
    print("🚀 IMEI API - FastAPI iniciando...")
    print("="*60)
    
    # Startup: Inicializar Google Sheets
    try:
        from app.services.sheets_service import SheetsService
        sheets_service = SheetsService()
        result = sheets_service.initialize_sheet()
        if result['success']:
            print("✅ Google Sheets inicializado correctamente")
        else:
            print(f"⚠️  Advertencia al inicializar Google Sheets: {result.get('error')}")
    except Exception as e:
        print(f"⚠️  No se pudo inicializar Google Sheets: {str(e)}")
    
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
            "http://localhost:3000",      # Frontend local (React/Next.js)
            "http://localhost:5173",      # Vite dev
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "*"                           # Permitir todos en desarrollo (cambiar en producción)
        ],
        allow_credentials=True,
        allow_methods=["*"],              # Permitir todos los métodos
        allow_headers=["*"],              # Permitir todos los headers
    )
    
    # ============ REGISTRAR RUTAS ============
    print("\n📋 Registrando rutas...")
    
    app.include_router(
        health.router,
        prefix="/api",
        tags=["health"]
    )
    print("   ✓ Health routes registradas (/api/health)")
    
    app.include_router(
        devices.router,
        prefix="/api/devices",
        tags=["devices"]
    )
    print("   ✓ Devices routes registradas (/api/devices/*)")
    
    app.include_router(
        sheets.router,
        prefix="/api/sheets",
        tags=["sheets"]
    )
    print("   ✓ Sheets routes registradas (/api/sheets/*)")
    
    # ============ ROOT ENDPOINT ============
    @app.get("/", tags=["root"])
    async def root():
        """Endpoint raíz de bienvenida"""
        return {
            "message": "IMEI API v2.0.0 - FastAPI",
            "status": "running",
            "docs": "/docs",
            "endpoints": {
                "health": "/api/health",
                "devices": "/api/devices/*",
                "sheets": "/api/sheets/*"
            }
        }
    
    # ============ ERROR HANDLERS ============
    @app.get("/api/health", tags=["health"])
    async def quick_health():
        """Health check rápido"""
        return {"status": "ok"}
    
    return app


# Crear instancia de la app
app = create_app()


if __name__ == "__main__":
    # Ejecutar con uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
