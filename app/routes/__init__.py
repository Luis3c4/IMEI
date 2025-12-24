from flask import Flask

def register_blueprints(app: Flask):
    """
    Registra todos los blueprints de la aplicación
    
    Args:
        app: Instancia de Flask
    """
    from .health import health_bp
    from .devices import devices_bp
    from .sheets import sheets_bp
    
    # Registrar con prefijos
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(devices_bp, url_prefix='/api/devices')
    app.register_blueprint(sheets_bp, url_prefix='/api/sheets')
    
    print("\n✓ Blueprints registrados:")
    print("  - Health:  /api/health")
    print("  - Devices: /api/devices/*")
    print("  - Sheets:  /api/sheets/*")
