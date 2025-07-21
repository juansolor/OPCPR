# opcua_client.py
"""
Módulo para manejar conexiones y operaciones con servidores OPC UA
"""

from opcua import Client
import logging

# Configurar logging
logging.basicConfig(level=logging.WARNING)

# Definir señales por defecto (esto puede ser configurado desde settings)
SIGNALS = [
    "ns=2;i=2",  # Ejemplo de node ID
    "ns=2;i=3",  # Ejemplo de node ID  
    "ns=2;i=4",  # Ejemplo de node ID
]

class OpcUaServer:
    """Clase para manejar conexiones con servidor OPC UA"""
    
    def __init__(self, url="opc.tcp://localhost:4840"):
        self.url = url
        self.client = None
        self.connected = False
    
    def connect(self):
        """Conectar al servidor OPC UA"""
        try:
            self.client = Client(self.url)
            self.client.connect()
            self.connected = True
            return True
        except Exception as e:
            print(f"Error conectando a OPC UA: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Desconectar del servidor OPC UA"""
        try:
            if self.client and self.connected:
                self.client.disconnect()
                self.connected = False
        except Exception as e:
            print(f"Error desconectando OPC UA: {e}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

def LeerOpcUa(url, signals):
    """
    Función para leer datos del servidor OPC UA
    
    Args:
        url (str): URL del servidor OPC UA
        signals (list): Lista de node IDs a leer
        
    Returns:
        dict: Diccionario con los datos leídos o None si hay error
    """
    try:
        with OpcUaServer(url) as server:
            if not server.connected:
                return None
            
            data = {}
            for signal in signals:
                try:
                    node = server.client.get_node(signal)
                    value = node.get_value()
                    data[signal] = value
                except Exception as e:
                    print(f"Error leyendo señal {signal}: {e}")
                    data[signal] = None
            
            return data
    
    except Exception as e:
        print(f"Error en LeerOpcUa: {e}")
        return None

def EscribirOpcUa(url, data):
    """
    Función para escribir datos al servidor OPC UA
    
    Args:
        url (str): URL del servidor OPC UA
        data (dict): Diccionario con node_id: valor a escribir
        
    Returns:
        dict: Resultado de la operación o None si hay error
    """
    try:
        with OpcUaServer(url) as server:
            if not server.connected:
                return None
            
            result = {
                "success": True,
                "written_nodes": 0,
                "errors": []
            }
            
            for node_id, value in data.items():
                try:
                    node = server.client.get_node(node_id)
                    node.set_value(value)
                    result["written_nodes"] += 1
                except Exception as e:
                    error_msg = f"Error escribiendo {node_id}: {e}"
                    print(error_msg)
                    result["errors"].append(error_msg)
                    result["success"] = False
            
            return result
    
    except Exception as e:
        print(f"Error en EscribirOpcUa: {e}")
        return None

# Función de ejemplo para simular datos cuando no hay servidor OPC UA
def simular_datos_opcua():
    """
    Función para simular datos cuando no hay servidor OPC UA disponible
    """
    import random
    
    return {
        "ns=2;i=2": round(random.uniform(20.0, 30.0), 2),  # Temperatura
        "ns=2;i=3": round(random.uniform(1000.0, 1020.0), 2),  # Presión
        "ns=2;i=4": round(random.uniform(70.0, 90.0), 2),  # Nivel
        "timestamp": "2025-07-21T16:00:00Z",
        "simulated": True
    }
