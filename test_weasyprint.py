"""
Script de prueba para verificar que WeasyPrint funciona correctamente
"""
from pathlib import Path
from io import BytesIO

def test_weasyprint_basico():
    """Prueba básica de WeasyPrint con HTML simple"""
    print("🔍 Probando importación de WeasyPrint...")
    try:
        from weasyprint import HTML, CSS
        print("✅ WeasyPrint importado correctamente")
    except ImportError as e:
        print(f"❌ Error importando WeasyPrint: {e}")
        return False
    
    print("\n🔍 Probando generación de PDF simple...")
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }
                h1 {
                    color: #007AFF;
                }
            </style>
        </head>
        <body>
            <h1>✅ WeasyPrint está funcionando!</h1>
            <p>Este es un PDF de prueba generado con WeasyPrint.</p>
            <p>Fecha: <strong>28 de diciembre de 2025</strong></p>
        </body>
        </html>
        """
        
        # Crear PDF en memoria
        html = HTML(string=html_content)
        pdf_buffer = BytesIO()
        html.write_pdf(pdf_buffer)
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        print(f"✅ PDF generado exitosamente ({len(pdf_bytes)} bytes)")
        
        # Guardar PDF de prueba
        output_path = Path("test_weasyprint_output.pdf")
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"✅ PDF guardado en: {output_path.absolute()}")
        
        return True
    except Exception as e:
        print(f"❌ Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_weasyprint_con_css():
    """Prueba WeasyPrint con CSS más complejo"""
    print("\n🔍 Probando generación de PDF con CSS avanzado...")
    try:
        from weasyprint import HTML, CSS
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {
                    size: A4;
                    margin: 2cm;
                }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                    line-height: 1.6;
                }
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }
                .info-box {
                    border: 2px solid #007AFF;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                }
                .success {
                    color: #34C759;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Prueba Avanzada de WeasyPrint</h1>
            </div>
            <div class="info-box">
                <h2>Características probadas:</h2>
                <ul>
                    <li>✅ Importación de módulos</li>
                    <li>✅ Generación de PDF básico</li>
                    <li>✅ Soporte de CSS3</li>
                    <li>✅ Fuentes del sistema</li>
                    <li>✅ Gradientes CSS</li>
                    <li>✅ Bordes y estilos</li>
                </ul>
            </div>
            <p class="success">¡Todas las pruebas pasaron correctamente!</p>
        </body>
        </html>
        """
        
        html = HTML(string=html_content)
        pdf_buffer = BytesIO()
        html.write_pdf(pdf_buffer)
        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        print(f"✅ PDF con CSS avanzado generado ({len(pdf_bytes)} bytes)")
        
        output_path = Path("test_weasyprint_advanced.pdf")
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"✅ PDF guardado en: {output_path.absolute()}")
        
        return True
    except Exception as e:
        print(f"❌ Error en prueba avanzada: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependencias():
    """Verifica que todas las dependencias de WeasyPrint estén instaladas"""
    print("\n🔍 Verificando dependencias de WeasyPrint...")
    
    dependencias = {
        'weasyprint': 'WeasyPrint',
        'cffi': 'CFFI (interfaz C)',
        'pycparser': 'PyParser',
        'pyphen': 'Pyphen (división de palabras)',
        'cssselect2': 'CSS Selector',
        'tinycss2': 'CSS Parser',
        'PIL': 'Pillow (imágenes)',
    }
    
    all_ok = True
    for modulo, nombre in dependencias.items():
        try:
            __import__(modulo)
            print(f"✅ {nombre}: instalado")
        except ImportError:
            print(f"❌ {nombre}: NO instalado")
            all_ok = False
    
    return all_ok


if __name__ == "__main__":
    print("="*60)
    print("  PRUEBA DE WEASYPRINT")
    print("="*60)
    
    # Verificar dependencias
    deps_ok = test_dependencias()
    
    if not deps_ok:
        print("\n⚠️  Algunas dependencias faltan. Instala con:")
        print("    pip install weasyprint")
        print("\nO si estás en Linux, también necesitas:")
        print("    sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0")
    
    # Prueba básica
    if deps_ok:
        test1_ok = test_weasyprint_basico()
        
        # Prueba avanzada
        if test1_ok:
            test2_ok = test_weasyprint_con_css()
            
            print("\n" + "="*60)
            if test1_ok and test2_ok:
                print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
                print("✅ WeasyPrint está funcionando perfectamente")
            else:
                print("⚠️  Algunas pruebas fallaron")
            print("="*60)
    else:
        print("\n❌ No se pueden ejecutar las pruebas sin las dependencias")
