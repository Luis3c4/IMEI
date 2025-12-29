"""
Script de prueba rápida para validar todos los endpoints
Ejecutar cuando el servidor FastAPI está corriendo
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_response(title: str, response: dict):
    """Imprime la respuesta de forma formateada"""
    print(f"\n{'='*60}")
    print(f"✓ {title}")
    print(f"{'='*60}")
    print(json.dumps(response, indent=2, ensure_ascii=False))

def test_health():
    """Prueba el endpoint de health check"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print_response("Health Check", response.json())
            return True
        else:
            print(f"❌ Health check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en health check: {str(e)}")
        return False

def test_balance():
    """Prueba obtener balance"""
    try:
        response = requests.get(f"{BASE_URL}/api/devices/balance")
        if response.status_code == 200:
            print_response("Balance de Cuenta", response.json())
            return True
        else:
            print(f"❌ Balance falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error obteniendo balance: {str(e)}")
        return False

def test_services():
    """Prueba obtener servicios"""
    try:
        response = requests.get(f"{BASE_URL}/api/devices/services")
        if response.status_code == 200:
            data = response.json()
            # Limitar la salida si hay muchos servicios
            if 'services' in data and len(data['services']) > 3:
                data['services'] = data['services'][:3]
                data['_truncated'] = True
            print_response("Servicios Disponibles", data)
            return True
        else:
            print(f"❌ Servicios falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error obteniendo servicios: {str(e)}")
        return False

def test_sheets_stats():
    """Prueba obtener estadísticas del sheet"""
    try:
        response = requests.get(f"{BASE_URL}/api/sheets/stats")
        if response.status_code == 200:
            print_response("Estadísticas del Sheet", response.json())
            return True
        else:
            print(f"❌ Stats falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error obteniendo stats: {str(e)}")
        return False

def test_sheets_url():
    """Prueba obtener URL del sheet"""
    try:
        response = requests.get(f"{BASE_URL}/api/sheets/url")
        if response.status_code == 200:
            print_response("URL del Google Sheet", response.json())
            return True
        else:
            print(f"❌ Sheet URL falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error obteniendo URL del sheet: {str(e)}")
        return False

def test_query_device():
    """Prueba consultar un dispositivo"""
    # IMEI válido de prueba (fake)
    test_imei = "356789012345678"
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/devices/consultar",
            json={
                "input_value": test_imei,
                "service_id": "30",
                "formato": "beta"
            }
        )
        if response.status_code == 200:
            print_response(f"Consulta de Dispositivo (IMEI: {test_imei})", response.json())
            return True
        else:
            print(f"⚠️  Consulta de dispositivo: {response.status_code}")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return False
    except Exception as e:
        print(f"⚠️  Error consultando dispositivo: {str(e)}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "="*60)
    print("🧪 PRUEBAS DE ENDPOINTS - FASTAPI IMEI")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Hora: {datetime.now().strftime('%H:%M:%S')}")
    
    results = {
        "Health Check": test_health(),
        "Balance": test_balance(),
        "Servicios": test_services(),
        "Sheet Stats": test_sheets_stats(),
        "Sheet URL": test_sheets_url(),
        "Consulta Dispositivo": test_query_device(),
    }
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASÓ" if passed_test else "⚠️  FALLÓ/ADVERTENCIA"
        print(f"{test_name:<25} {status}")
    
    print(f"\nTotal: {passed}/{total} endpoints funcionales")
    
    if passed == total:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    else:
        print(f"\n⚠️  {total - passed} prueba(s) con advertencia")
    
    print("="*60)

if __name__ == "__main__":
    main()
