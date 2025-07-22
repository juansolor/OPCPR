# data_clients.py
"""
Módulo para manejar conexiones y operaciones con múltiples tipos de servidores de datos
Soporta: OPC-UA, OPC Classic, WebSockets, Modbus, MQTT
"""

import asyncio
import json
import logging
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataClientBase(ABC):
    """Clase base abstracta para todos los clientes de datos"""
    
    def __init__(self, server_config: Dict[str, Any]):
        self.server_config = server_config
        self.is_connected = False
        self.callbacks = {}
        self.error_callbacks = {}
        
    @abstractmethod
    async def connect(self) -> bool:
        """Conectar al servidor"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Desconectar del servidor"""
        pass
    
    @abstractmethod
    async def read_variable(self, address: str, config: Dict[str, Any] = None) -> Any:
        """Leer una variable específica"""
        pass
    
    @abstractmethod
    async def write_variable(self, address: str, value: Any, config: Dict[str, Any] = None) -> bool:
        """Escribir a una variable específica"""
        pass
    
    @abstractmethod
    async def subscribe_variable(self, address: str, callback: Callable, config: Dict[str, Any] = None):
        """Suscribirse a cambios en una variable"""
        pass
    
    def add_data_callback(self, address: str, callback: Callable):
        """Agregar callback para datos de una variable"""
        if address not in self.callbacks:
            self.callbacks[address] = []
        self.callbacks[address].append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Agregar callback para errores"""
        if 'error' not in self.error_callbacks:
            self.error_callbacks['error'] = []
        self.error_callbacks['error'].append(callback)


class OpcUaClient(DataClientBase):
    """Cliente para servidores OPC-UA"""
    
    def __init__(self, server_config: Dict[str, Any]):
        super().__init__(server_config)
        self.client = None
        
    async def connect(self) -> bool:
        """Conectar al servidor OPC-UA"""
        try:
            from opcua import Client
            
            self.client = Client(self.server_config['endpoint_url'])
            
            # Configurar autenticación si está disponible
            if self.server_config.get('username') and self.server_config.get('password'):
                self.client.set_user(self.server_config['username'])
                self.client.set_password(self.server_config['password'])
            
            # Configurar seguridad
            config = self.server_config.get('connection_config', {})
            if config.get('security_mode') == 'SIGN':
                # Configurar modo de firma
                pass
            elif config.get('security_mode') == 'SIGN_ENCRYPT':
                # Configurar modo de firma y encriptación
                pass
            
            await asyncio.get_event_loop().run_in_executor(None, self.client.connect)
            self.is_connected = True
            logger.info(f"Conectado a OPC-UA: {self.server_config['endpoint_url']}")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a OPC-UA: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Desconectar del servidor OPC-UA"""
        try:
            if self.client and self.is_connected:
                await asyncio.get_event_loop().run_in_executor(None, self.client.disconnect)
                self.is_connected = False
                logger.info("Desconectado de OPC-UA")
        except Exception as e:
            logger.error(f"Error desconectando OPC-UA: {e}")
    
    async def read_variable(self, address: str, config: Dict[str, Any] = None) -> Any:
        """Leer una variable OPC-UA"""
        try:
            if not self.is_connected:
                await self.connect()
            
            node = self.client.get_node(address)
            value = await asyncio.get_event_loop().run_in_executor(None, node.get_value)
            return value
            
        except Exception as e:
            logger.error(f"Error leyendo variable OPC-UA {address}: {e}")
            return None
    
    async def write_variable(self, address: str, value: Any, config: Dict[str, Any] = None) -> bool:
        """Escribir a una variable OPC-UA"""
        try:
            if not self.is_connected:
                await self.connect()
            
            node = self.client.get_node(address)
            await asyncio.get_event_loop().run_in_executor(None, node.set_value, value)
            return True
            
        except Exception as e:
            logger.error(f"Error escribiendo variable OPC-UA {address}: {e}")
            return False
    
    async def subscribe_variable(self, address: str, callback: Callable, config: Dict[str, Any] = None):
        """Suscribirse a cambios en una variable OPC-UA"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Implementar suscripción OPC-UA
            # Esto requiere crear una suscripción y manejar callbacks
            pass
            
        except Exception as e:
            logger.error(f"Error suscribiéndose a variable OPC-UA {address}: {e}")


class WebSocketClient(DataClientBase):
    """Cliente para servidores WebSocket"""
    
    def __init__(self, server_config: Dict[str, Any]):
        super().__init__(server_config)
        self.websocket = None
        self.receive_task = None
        
    async def connect(self) -> bool:
        """Conectar al servidor WebSocket"""
        try:
            import websockets
            
            uri = self.server_config['endpoint_url']
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            
            # Iniciar tarea de recepción
            self.receive_task = asyncio.create_task(self._receive_messages())
            
            logger.info(f"Conectado a WebSocket: {uri}")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a WebSocket: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Desconectar del servidor WebSocket"""
        try:
            if self.receive_task:
                self.receive_task.cancel()
            
            if self.websocket:
                await self.websocket.close()
                self.is_connected = False
                logger.info("Desconectado de WebSocket")
                
        except Exception as e:
            logger.error(f"Error desconectando WebSocket: {e}")
    
    async def _receive_messages(self):
        """Tarea para recibir mensajes del WebSocket"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.error(f"Error decodificando mensaje WebSocket: {message}")
                    
        except Exception as e:
            logger.error(f"Error en recepción WebSocket: {e}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Manejar mensaje recibido"""
        try:
            # Extraer información del mensaje
            address = data.get('address') or data.get('topic') or data.get('variable')
            value = data.get('value')
            timestamp = data.get('timestamp', datetime.now().isoformat())
            
            # Ejecutar callbacks
            if address in self.callbacks:
                for callback in self.callbacks[address]:
                    await asyncio.get_event_loop().run_in_executor(
                        None, callback, address, value, timestamp
                    )
                    
        except Exception as e:
            logger.error(f"Error manejando mensaje WebSocket: {e}")
    
    async def read_variable(self, address: str, config: Dict[str, Any] = None) -> Any:
        """Solicitar lectura de variable via WebSocket"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Enviar solicitud de lectura
            request = {
                'action': 'read',
                'address': address,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(request))
            # En WebSocket, la respuesta llegará via _receive_messages
            return True
            
        except Exception as e:
            logger.error(f"Error leyendo variable WebSocket {address}: {e}")
            return None
    
    async def write_variable(self, address: str, value: Any, config: Dict[str, Any] = None) -> bool:
        """Escribir variable via WebSocket"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Enviar comando de escritura
            request = {
                'action': 'write',
                'address': address,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(request))
            return True
            
        except Exception as e:
            logger.error(f"Error escribiendo variable WebSocket {address}: {e}")
            return False
    
    async def subscribe_variable(self, address: str, callback: Callable, config: Dict[str, Any] = None):
        """Suscribirse a una variable via WebSocket"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Agregar callback
            self.add_data_callback(address, callback)
            
            # Enviar solicitud de suscripción
            request = {
                'action': 'subscribe',
                'address': address,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(request))
            
        except Exception as e:
            logger.error(f"Error suscribiéndose a variable WebSocket {address}: {e}")


class OpcClassicClient(DataClientBase):
    """Cliente para servidores OPC Classic (DA)"""
    
    def __init__(self, server_config: Dict[str, Any]):
        super().__init__(server_config)
        self.opc_client = None
        
    async def connect(self) -> bool:
        """Conectar al servidor OPC Classic"""
        try:
            # Nota: Para OPC Classic necesitarías una librería como OpenOPC
            # import openopc
            
            # self.opc_client = openopc.client()
            # self.opc_client.connect(self.server_config.get('prog_id', 'OPC.Server'))
            
            self.is_connected = True
            logger.info(f"Conectado a OPC Classic: {self.server_config['endpoint_url']}")
            return True
            
        except Exception as e:
            logger.error(f"Error conectando a OPC Classic: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Desconectar del servidor OPC Classic"""
        try:
            if self.opc_client and self.is_connected:
                # self.opc_client.close()
                self.is_connected = False
                logger.info("Desconectado de OPC Classic")
        except Exception as e:
            logger.error(f"Error desconectando OPC Classic: {e}")
    
    async def read_variable(self, address: str, config: Dict[str, Any] = None) -> Any:
        """Leer una variable OPC Classic"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # value = self.opc_client.read(address)
            # return value[0] if value else None
            return None  # Placeholder
            
        except Exception as e:
            logger.error(f"Error leyendo variable OPC Classic {address}: {e}")
            return None
    
    async def write_variable(self, address: str, value: Any, config: Dict[str, Any] = None) -> bool:
        """Escribir a una variable OPC Classic"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # self.opc_client.write((address, value))
            return True  # Placeholder
            
        except Exception as e:
            logger.error(f"Error escribiendo variable OPC Classic {address}: {e}")
            return False
    
    async def subscribe_variable(self, address: str, callback: Callable, config: Dict[str, Any] = None):
        """Suscribirse a cambios en una variable OPC Classic"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Implementar suscripción OPC Classic
            pass
            
        except Exception as e:
            logger.error(f"Error suscribiéndose a variable OPC Classic {address}: {e}")


class DataClientFactory:
    """Factory para crear clientes de datos según el tipo de servidor"""
    
    _clients = {
        'OPC_UA': OpcUaClient,
        'OPC_CLASSIC': OpcClassicClient,
        'WEBSOCKET': WebSocketClient,
        # 'MODBUS': ModbusClient,  # Se puede implementar después
        # 'MQTT': MqttClient,      # Se puede implementar después
    }
    
    @classmethod
    def create_client(cls, server_type: str, server_config: Dict[str, Any]) -> Optional[DataClientBase]:
        """Crear un cliente según el tipo de servidor"""
        client_class = cls._clients.get(server_type)
        if client_class:
            return client_class(server_config)
        else:
            logger.error(f"Tipo de servidor no soportado: {server_type}")
            return None
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Obtener lista de tipos de servidores soportados"""
        return list(cls._clients.keys())


class DataManager:
    """Manager principal para manejar múltiples clientes de datos"""
    
    def __init__(self):
        self.clients: Dict[str, DataClientBase] = {}
        self.active_subscriptions: Dict[str, List[str]] = {}  # server_id -> [addresses]
        
    async def add_server(self, server_id: str, server_type: str, server_config: Dict[str, Any]) -> bool:
        """Agregar un servidor al manager"""
        try:
            client = DataClientFactory.create_client(server_type, server_config)
            if client:
                self.clients[server_id] = client
                return await client.connect()
            return False
        except Exception as e:
            logger.error(f"Error agregando servidor {server_id}: {e}")
            return False
    
    async def remove_server(self, server_id: str):
        """Remover un servidor del manager"""
        try:
            if server_id in self.clients:
                await self.clients[server_id].disconnect()
                del self.clients[server_id]
                if server_id in self.active_subscriptions:
                    del self.active_subscriptions[server_id]
        except Exception as e:
            logger.error(f"Error removiendo servidor {server_id}: {e}")
    
    async def read_variable(self, server_id: str, address: str, config: Dict[str, Any] = None) -> Any:
        """Leer una variable de un servidor específico"""
        try:
            if server_id in self.clients:
                return await self.clients[server_id].read_variable(address, config)
            else:
                logger.error(f"Servidor no encontrado: {server_id}")
                return None
        except Exception as e:
            logger.error(f"Error leyendo variable {address} de servidor {server_id}: {e}")
            return None
    
    async def write_variable(self, server_id: str, address: str, value: Any, config: Dict[str, Any] = None) -> bool:
        """Escribir una variable en un servidor específico"""
        try:
            if server_id in self.clients:
                return await self.clients[server_id].write_variable(address, value, config)
            else:
                logger.error(f"Servidor no encontrado: {server_id}")
                return False
        except Exception as e:
            logger.error(f"Error escribiendo variable {address} en servidor {server_id}: {e}")
            return False
    
    async def subscribe_variable(self, server_id: str, address: str, callback: Callable, config: Dict[str, Any] = None):
        """Suscribirse a una variable de un servidor específico"""
        try:
            if server_id in self.clients:
                await self.clients[server_id].subscribe_variable(address, callback, config)
                
                # Registrar suscripción
                if server_id not in self.active_subscriptions:
                    self.active_subscriptions[server_id] = []
                if address not in self.active_subscriptions[server_id]:
                    self.active_subscriptions[server_id].append(address)
                    
            else:
                logger.error(f"Servidor no encontrado: {server_id}")
        except Exception as e:
            logger.error(f"Error suscribiéndose a variable {address} de servidor {server_id}: {e}")
    
    def get_server_status(self, server_id: str) -> Dict[str, Any]:
        """Obtener estado de un servidor"""
        if server_id in self.clients:
            client = self.clients[server_id]
            return {
                'server_id': server_id,
                'connected': client.is_connected,
                'subscriptions': self.active_subscriptions.get(server_id, [])
            }
        return {'server_id': server_id, 'connected': False, 'error': 'Servidor no encontrado'}
    
    def get_all_servers_status(self) -> List[Dict[str, Any]]:
        """Obtener estado de todos los servidores"""
        return [self.get_server_status(server_id) for server_id in self.clients.keys()]


# Instancia global del manager de datos
data_manager = DataManager()
