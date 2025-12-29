#!/usr/bin/env python3
"""
Script de validación de dependencias
Verifica que todas las bibliotecas necesarias estén instaladas correctamente
"""

import sys
from typing import List, Tuple

def check_dependencies() -> List[Tuple[str, bool, str]]:
    """Verifica todas las dependencias del proyecto"""
    results = []
    
    # Lista de dependencias a verificar
    dependencies = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pydantic', 'Pydantic'),
        ('pydantic_settings', 'Pydantic Settings'),
        ('dotenv', 'Python Dotenv'),
        ('requests', 'Requests'),
        ('httpx', 'HTTPX'),
        ('gspread', 'Gspread'),
        ('google.oauth2', 'Google Auth'),
        ('googleapiclient', 'Google API Client'),
        ('weasyprint', 'Weasyprint'),
        ('jinja2', 'Jinja2'),
    ]
    
    print("\n" + "="*60)
    print("🔍 VALIDACIÓN DE DEPENDENCIAS")
    print("="*60 + "\n")
    
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            results.append((display_name, True, "OK"))
            print(f"✅ {display_name:<30} Instalado")
        except ImportError as e:
            results.append((display_name, False, str(e)))
            print(f"❌ {display_name:<30} NO ENCONTRADO")
        except Exception as e:
            results.append((display_name, False, str(e)))
            print(f"⚠️  {display_name:<30} ERROR: {str(e)[:40]}")
    
    return results

def check_system_libraries():
    """Verifica bibliotecas del sistema necesarias para Weasyprint"""
    print("\n" + "="*60)
    print("🔍 VALIDACIÓN DE BIBLIOTECAS DEL SISTEMA (Weasyprint)")
    print("="*60 + "\n")
    
    try:
        import cairocffi
        print("✅ Cairo (cairocffi) - OK")
        return True
    except ImportError:
        print("❌ Cairo (cairocffi) - NO ENCONTRADO")
        print("\n⚠️  Necesitas instalar dependencias del sistema:")
        print("   sudo apt-get install libcairo2 libpango-1.0-0 libpangocairo-1.0-0")
        return False
    except Exception as e:
        print(f"⚠️  Error al verificar Cairo: {str(e)}")
        return False

def test_weasyprint():
    """Prueba funcional de Weasyprint"""
    print("\n" + "="*60)
    print("🧪 PRUEBA FUNCIONAL DE WEASYPRINT")
    print("="*60 + "\n")
    
    try:
        from weasyprint import HTML
        
        # Crear un HTML simple
        html_content = "<html><body><h1>Test</h1></body></html>"
        document = HTML(string=html_content)
        
        # Intentar generar PDF
        pdf_bytes = document.write_pdf()
        
        if pdf_bytes and len(pdf_bytes) > 0:
            print("✅ Weasyprint puede generar PDFs correctamente")
            print(f"   PDF de prueba generado: {len(pdf_bytes)} bytes")
            return True
        else:
            print("❌ Weasyprint no pudo generar el PDF")
            return False
            
    except Exception as e:
        print(f"❌ Error al probar Weasyprint: {str(e)}")
        return False

def main():
    """Función principal"""
    # Verificar dependencias Python
    results = check_dependencies()
    
    # Verificar bibliotecas del sistema
    system_ok = check_system_libraries()
    
    # Probar Weasyprint
    weasyprint_ok = test_weasyprint()
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60 + "\n")
    
    total = len(results)
    success = sum(1 for _, ok, _ in results if ok)
    failed = total - success
    
    print(f"Total de dependencias: {total}")
    print(f"✅ Instaladas correctamente: {success}")
    print(f"❌ Faltantes o con error: {failed}")
    
    if failed == 0 and system_ok and weasyprint_ok:
        print("\n🎉 ¡Todas las dependencias están instaladas correctamente!")
        print("   Puedes ejecutar el servidor con: python main.py")
        return 0
    else:
        print("\n⚠️  Algunas dependencias faltan o tienen problemas")
        print("   Ejecuta: ./install_dependencies.sh")
        print("   O revisa: INSTALL_WSL.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())
