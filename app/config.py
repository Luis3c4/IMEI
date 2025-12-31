import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación FastAPI
    Las variables se cargan desde .env o variables de entorno
    """
    
    # ============ DHRU API ============
    DHRU_API_KEY: str = os.getenv('DHRU_API_KEY', '1PA-6X8-BMQ-T28-X6H-8WP-7CL-GTK')
    DHRU_API_USER: str = os.getenv('DHRU_API_USER', 'javie.apaza@gmail.com')
    DHRU_API_BASE: str = 'https://sickw.com/api.php'
    
    # ============ RENIEC API ============
    RENIEC_API_BASE: str = 'https://api.decolecta.com/v1/reniec'
    RENIEC_API_TOKEN: str = os.getenv('RENIEC_API_TOKEN', 'sk_12581.twCsX39rBPOY9qvlixjVn9rWAR4L1diH')
    
    # ============ GOOGLE SHEETS ============
    GOOGLE_SHEET_ID: str = os.getenv('GOOGLE_SHEET_ID', '1e1P39zCbyfPD7jg_RbnEAzm_ZfOe7B5_VDVBQCZnjZM')
    GOOGLE_CREDENTIALS_JSON: Optional[str] = os.getenv('GOOGLE_CREDENTIALS_JSON', None)
    
    # ============ SUPABASE (OPCIONAL) ============
    SUPABASE_URL: Optional[str] = os.getenv('SUPABASE_URL', None)
    SUPABASE_KEY: Optional[str] = os.getenv('SUPABASE_KEY', None)
    SUPABASE_TABLE_DEVICES: str = "devices"
    SUPABASE_TABLE_HISTORY: str = "consulta_history"
    SUPABASE_TABLE_PRODUCTS: str = "products"
    
    # ============ APPLICATION ============
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '8000'))
    ENV: str = os.getenv('ENV', 'development')
    
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