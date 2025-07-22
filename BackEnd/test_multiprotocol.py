# test_multiprotocol.py
"""
Script de prueba para el sistema multi-protocolo
Demuestra cómo usar los nuevos clientes para diferentes protocolos
"""

import asyncio
import json
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_app.data_clients import DataManager, DataClientFactory

async def test_websocket_client():
    """Probar cliente WebSocket"""
    print("\n=== PROBANDO CLIENTE WEBSOCKET ===")
    
    # Configuración del servidor WebSocket
    server_config = {
        'endpoint_url': 'ws://localhost:8765',
        'connection_config': {
            'protocol': 'ws',
            'heartbeat_interval': 30,
            'reconnect_attempts': 5
        }
    }
    
    # Crear cliente
    client = DataClientFactory.create_client('WEBSOCKET', server_config)
    
    if client:
        print("Cliente WebSocket creado exitosamente")
        
        # Probar conexión
        print("Conectando al servidor WebSocket...")
        success = await client.connect()
        
        if success:
            print("✅ Conectado al servidor WebSocket")
            
            # Definir callback para datos
            def data_callback(address, value, timestamp):
                print(f"📊 Dato recibido - {address}: {value} ({timestamp})")
            
            # Suscribirse a variables
            variables = ['temperature_1', 'pressure_1', 'motor_1_status']
            
            for var in variables:
                print(f"Suscribiéndose a {var}...")
                await client.subscribe_variable(var, data_callback)
            
            # Leer algunas variables
            for var in variables:
                print(f"Leyendo {var}...")
                value = await client.read_variable(var)
                print(f"  Valor: {value}")
            
            # Escribir a una variable
            print("Escribiendo a motor_1_status...")
            success = await client.write_variable('motor_1_status', False)
            print(f"  Escritura {'exitosa' if success else 'falló'}")
            
            # Esperar un poco para recibir datos
            print("Esperando datos por 10 segundos...")
            await asyncio.sleep(10)
            
            # Desconectar
            await client.disconnect()
            print("✅ Desconectado del servidor WebSocket")
            
        else:
            print("❌ No se pudo conectar al servidor WebSocket")
            print("   Asegúrate de que el servidor WebSocket esté ejecutándose")
            print("   Ejecuta: python websocket_server_example.py")
    else:
        print("❌ No se pudo crear el cliente WebSocket")


async def test_opcua_client():
    """Probar cliente OPC-UA"""
    print("\n=== PROBANDO CLIENTE OPC-UA ===")
    
    # Configuración del servidor OPC-UA
    server_config = {
        'endpoint_url': 'opc.tcp://localhost:4840',
        'connection_config': {
            'security_mode': 'NONE',
            'certificate_path': '',
            'private_key_path': ''
        }
    }
    
    # Crear cliente
    client = DataClientFactory.create_client('OPC_UA', server_config)
    
    if client:
        print("Cliente OPC-UA creado exitosamente")
        
        # Probar conexión
        print("Conectando al servidor OPC-UA...")
        success = await client.connect()
        
        if success:
            print("✅ Conectado al servidor OPC-UA")
            
            # Probar lectura de variables comunes
            test_nodes = [
                'ns=2;i=2',  # Ejemplo de node ID
                'ns=2;i=3',
                'ns=0;i=2259'  # Server.ServerStatus.CurrentTime
            ]
            
            for node in test_nodes:
                print(f"Leyendo {node}...")
                try:
                    value = await client.read_variable(node)
                    print(f"  Valor: {value}")
                except Exception as e:
                    print(f"  Error: {e}")
            
            # Desconectar
            await client.disconnect()
            print("✅ Desconectado del servidor OPC-UA")
            
        else:
            print("❌ No se pudo conectar al servidor OPC-UA")
            print("   Asegúrate de que haya un servidor OPC-UA ejecutándose en localhost:4840")
    else:
        print("❌ No se pudo crear el cliente OPC-UA")


async def test_data_manager():
    """Probar el DataManager con múltiples servidores"""
    print("\n=== PROBANDO DATA MANAGER ===")
    
    manager = DataManager()
    
    # Configurar servidores
    servers = {
        'websocket_server': {
            'type': 'WEBSOCKET',
            'config': {
                'endpoint_url': 'ws://localhost:8765',
                'connection_config': {'protocol': 'ws'}
            }
        },
        'opcua_server': {
            'type': 'OPC_UA',
            'config': {
                'endpoint_url': 'opc.tcp://localhost:4840',
                'connection_config': {'security_mode': 'NONE'}
            }
        }
    }
    
    # Agregar servidores al manager
    for server_id, server_info in servers.items():
        print(f"Agregando servidor {server_id}...")
        success = await manager.add_server(
            server_id,
            server_info['type'],
            server_info['config']
        )
        
        if success:
            print(f"✅ Servidor {server_id} agregado y conectado")
        else:
            print(f"❌ No se pudo agregar servidor {server_id}")
    
    # Obtener estado de todos los servidores
    print("\nEstado de servidores:")
    all_status = manager.get_all_servers_status()
    for status in all_status:
        server_id = status['server_id']
        connected = status['connected']
        status_icon = "✅" if connected else "❌"
        print(f"  {status_icon} {server_id}: {'Conectado' if connected else 'Desconectado'}")
    
    # Probar lectura desde diferentes servidores
    if 'websocket_server' in manager.clients:
        print("\nProbando lectura desde WebSocket...")
        value = await manager.read_variable('websocket_server', 'temperature_1')
        print(f"  temperature_1: {value}")
    
    # Limpiar
    print("\nDesconectando servidores...")
    for server_id in servers.keys():
        await manager.remove_server(server_id)
    
    print("✅ Prueba del DataManager completada")


async def main():
    """Función principal de prueba"""
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA MULTI-PROTOCOLO")
    print("=" * 60)
    
    # Mostrar protocolos soportados
    supported = DataClientFactory.get_supported_types()
    print(f"Protocolos soportados: {', '.join(supported)}")
    
    try:
        # Probar clientes individuales
        await test_websocket_client()
        await test_opcua_client()
        
        # Probar manager
        await test_data_manager()
        
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
        
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Para ejecutar estas pruebas:")
    print("1. Instala las dependencias: pip install websockets opcua")
    print("2. Ejecuta el servidor WebSocket de ejemplo en otra terminal:")
    print("   python websocket_server_example.py")
    print("3. Opcionalmente, ejecuta un servidor OPC-UA en localhost:4840")
    print("4. Ejecuta este script: python test_multiprotocol.py")
    print()
    
    # Verificar si las librerías están disponibles
    try:
        import websockets
        print("✅ websockets disponible")
    except ImportError:
        print("❌ websockets no disponible - instalar con: pip install websockets")
    
    try:
        import opcua
        print("✅ opcua disponible")
    except ImportError:
        print("❌ opcua no disponible - instalar con: pip install opcua")
    
    print("\nEjecutando pruebas...\n")
    asyncio.run(main())
