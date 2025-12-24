from flask import Flask
from flask_cors import CORS

def create_app(config_name='default'):
    """
    Crea y configura la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Flask app configurada
    """
    app = Flask(__name__)
    
    # Cargar configuración
    from .config import config
    app.config.from_object(config[config_name])
    
    # Configurar CORS
    CORS(app)
    
    # Registrar blueprints
    from .routes import register_blueprints
    register_blueprints(app)
    
    # Inicializar Google Sheets
    from .services.sheets_service import SheetsService
    sheets_service = SheetsService()
    
    with app.app_context():
        result = sheets_service.initialize_sheet()
        if result['success']:
            print(" Google Sheet inicializado correctamente")
        else:
            print(" No se pudo inicializar Google Sheet")
    
    return app