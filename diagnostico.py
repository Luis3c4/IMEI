#!/usr/bin/env python3
"""
Diagnóstico del problema de importación de weasyprint
"""
import sys
import os

print("="*60)
print("DIAGNÓSTICO DE ENTORNO PYTHON")
print("="*60)
print(f"\n1. Python ejecutable: {sys.executable}")
print(f"2. Versión de Python: {sys.version}")
print(f"3. Directorio actual: {os.getcwd()}")
print(f"\n4. sys.path (rutas de búsqueda de módulos):")
for i, path in enumerate(sys.path, 1):
    print(f"   [{i}] {path}")

print("\n" + "="*60)
print("VERIFICACIÓN DE DEPENDENCIAS")
print("="*60)

dependencias = [
    'fastapi',
    'uvicorn', 
    'gspread',
    'weasyprint',
    'jinja2',
    'requests'
]

for dep in dependencias:
    try:
        mod = __import__(dep)
        version = getattr(mod, '__version__', 'N/A')
        print(f"✅ {dep:<15} v{version}")
    except ImportError as e:
        print(f"❌ {dep:<15} NO INSTALADO - {str(e)}")

print("\n" + "="*60)
print("SOLUCIÓN")
print("="*60)

# Detectar si estamos en un entorno virtual
in_venv = hasattr(sys, 'real_prefix') or (
    hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
)

if not in_venv:
    print("⚠️  NO estás en un entorno virtual")
    print("\nEjecuta estos comandos en WSL:")
    print("   cd /mnt/e/luis/Documents/javi-project/IMEI")
    print("   source venv/bin/activate")
    print("   pip install -r requirements.txt")
else:
    print("✅ Estás en un entorno virtual")
    print(f"   Ubicación: {sys.prefix}")
    
print("\n" + "="*60)
