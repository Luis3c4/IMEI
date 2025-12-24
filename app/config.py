import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Keys
    DHRU_API_KEY: str = os.getenv('DHRU_API_KEY', '1PA-6X8-BMQ-T28-X6H-8WP-7CL-GTK')
    DHRU_API_USER: str = os.getenv('DHRU_API_USER', 'javie.apaza@gmail.com')
    DHRU_API_BASE: str = 'https://sickw.com/api.php'
    
    # Google
    GOOGLE_SHEET_ID: str = os.getenv('GOOGLE_SHEET_ID', '1e1P39zCbyfPD7jg_RbnEAzm_ZfOe7B5_VDVBQCZnjZM')
    GOOGLE_CREDENTIALS_JSON: str | None = None
    
    # App
    DEBUG: bool = False
    HOST: str = '0.0.0.0'
    PORT: int = 5000
    
    # Redis para cache 
    REDIS_URL: str | None = None
    
    class Config:
        env_file = '.env'

settings = Settings()

# Configuración para diferentes entornos
class DevelopmentConfig(Settings):
    DEBUG: bool = True

class ProductionConfig(Settings):
    DEBUG: bool = False

class TestingConfig(Settings):
    DEBUG: bool = True
    TESTING: bool = True

# Diccionario de configuraciones
config = {
    'default': settings,
    'development': DevelopmentConfig(),
    'production': ProductionConfig(),
    'testing': TestingConfig()
}