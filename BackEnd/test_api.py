#!/usr/bin/env python3
"""
Script de ejemplo para probar la API del Supervisorio OPC UA
"""

import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health_check():
    """Prueba el endpoint de health check"""
    print("🔍 Probando Health Check...")
    try:
        response = requests.get(f"{API_BASE}/health/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check OK: {data['message']}")
            return True
        else:
            print(f"❌ Health Check falló: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error en Health Check: {e}")
        return False

def test_supervisorio_get():
    """Prueba la lectura de datos del supervisorio OPC UA"""
    print("\n📖 Probando lectura de datos OPC UA (GET)...")
    
    # Test con URL por defecto
    try:
        response = requests.get(f"{API_BASE}/supervisorio/")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Lectura exitosa")
        else:
            print("⚠️ Lectura falló (posiblemente no hay servidor OPC UA)")
            
    except Exception as e:
        print(f"❌ Error en lectura: {e}")
    
    # Test con URL personalizada
    print("\n📖 Probando con URL personalizada...")
    try:
        custom_url = "opc.tcp://192.168.1.100:4840"
        response = requests.get(f"{API_BASE}/supervisorio/?url={custom_url}")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ Error en lectura con URL personalizada: {e}")

def test_supervisorio_post():
    """Prueba la escritura de datos al supervisorio OPC UA"""
    print("\n✏️ Probando escritura de datos OPC UA (POST)...")
    
    # Datos de prueba
    test_data = {
        "url": "opc.tcp://localhost:4840",
        "data": {
            "setpoint_temperatura": 25.5,
            "setpoint_presion": 1013.25,
            "comando_bomba": True,
            "nivel_deseado": 80.0
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/supervisorio/",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Escritura exitosa")
        else:
            print("⚠️ Escritura falló (posiblemente no hay servidor OPC UA)")
            
    except Exception as e:
        print(f"❌ Error en escritura: {e}")

def test_supervisorio_post_without_data():
    """Prueba POST sin datos para verificar validación"""
    print("\n🚫 Probando POST sin datos (debe fallar)...")
    
    try:
        response = requests.post(
            f"{API_BASE}/supervisorio/",
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 400:
            print("✅ Validación correcta - Error esperado")
        else:
            print("❌ Validación incorrecta")
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de la API del Supervisorio OPC UA")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    if not test_health_check():
        print("\n❌ El servidor no está disponible. Asegúrate de que Django esté corriendo.")
        return
    
    # Ejecutar todas las pruebas
    test_supervisorio_get()
    test_supervisorio_post()
    test_supervisorio_post_without_data()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("\n💡 Notas:")
    print("- Los errores 500 son esperados si no hay un servidor OPC UA corriendo")
    print("- Para pruebas completas, configura un servidor OPC UA en opc.tcp://localhost:4840")

if __name__ == "__main__":
    main()
