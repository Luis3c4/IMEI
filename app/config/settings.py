import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Cargar .env.local si existe (desarrollo), sino cargar .env
env_file = Path(__file__).parent.parent.parent / '.env.local'
if not env_file.exists():
    env_file = Path(__file__).parent.parent.parent / '.env'

class Settings(BaseSettings):
    """
    Configuración de la aplicación FastAPI
    Las variables se cargan desde .env o .env.local según el entorno
    """
    
    # ============ DHRU API ============
    DHRU_API_KEY: str = os.getenv('DHRU_API_KEY', '')
    DHRU_API_USER: str = os.getenv('DHRU_API_USER', '')
    DHRU_API_BASE: str = 'https://sickw.com/api.php'
    
    # ============ RENIEC API ============
    RENIEC_API_BASE: str = 'https://api.decolecta.com/v1/reniec'
    RENIEC_API_TOKEN: str = os.getenv('RENIEC_API_TOKEN', '')
    
    # ============ GOOGLE SHEETS ============
    GOOGLE_SHEET_ID: str = os.getenv('GOOGLE_SHEET_ID', '')
    GOOGLE_CREDENTIALS_JSON: Optional[str] = os.getenv('GOOGLE_CREDENTIALS_JSON', None)
    
    # ============ SUPABASE (OPCIONAL) ============
    SUPABASE_URL: Optional[str] = os.getenv('SUPABASE_URL', None)
    SUPABASE_KEY: Optional[str] = os.getenv('SUPABASE_KEY', None)  # Service Role Key (para operaciones de backend)
    SUPABASE_ANON_KEY: Optional[str] = os.getenv('SUPABASE_ANON_KEY', None)  # Anon Key (para validación JWT)
    
    # Nota: Los nombres de tablas se usan como literales en el código.
    
    # ============ APPLICATION ============
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '8000'))
    ENV: str = os.getenv('ENV', 'production')
    
    # ============ REDIS (OPCIONAL) ============
    REDIS_URL: Optional[str] = os.getenv('REDIS_URL', None)
    
    class Config:
        env_file = '.env'
        case_sensitive = True


# Instancia global de configuración
settings = Settings()


# Configuraciones para diferentes entornos (opcional)
class DevelopmentConfig(Settings):
    DEBUG: bool = True
    ENV: str = 'development'


class ProductionConfig(Settings):
    DEBUG: bool = False
    ENV: str = 'production'


class TestingConfig(Settings):
    DEBUG: bool = True
    ENV: str = 'testing'


# Diccionario de configuraciones
config_dict = {
    'default': settings,
    'development': DevelopmentConfig(),
    'production': ProductionConfig(),
    'testing': TestingConfig()
}