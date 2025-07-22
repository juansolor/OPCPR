# websocket_server_example.py
"""
Servidor WebSocket de ejemplo para probar el sistema multi-protocolo
Este servidor simula un sistema industrial enviando datos de variables
"""

import asyncio
import json
import logging
import random
import time
from datetime import datetime
from typing import Dict, Set
import websockets

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IndustrialWebSocketServer:
    """Servidor WebSocket que simula un sistema industrial"""
    
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.subscriptions: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.variables = self._init_variables()
        self.running = False
        
    def _init_variables(self):
        """Inicializar variables simuladas"""
        return {
            'temperature_1': {
                'value': 25.0,
                'min': 20.0,
                'max': 80.0,
                'variation': 2.0,
                'unit': '°C',
                'type': 'float'
            },
            'pressure_1': {
                'value': 1013.25,
                'min': 950.0,
                'max': 1100.0,
                'variation': 10.0,
                'unit': 'hPa',
                'type': 'float'
            },
            'motor_1_status': {
                'value': True,
                'type': 'boolean'
            },
            'production_count': {
                'value': 1500,
                'min': 0,
                'max': 10000,
                'variation': 5,
                'unit': 'units',
                'type': 'integer'
            },
            'alarm_status': {
                'value': 'OK',
                'options': ['OK', 'WARNING', 'ALARM', 'CRITICAL'],
                'type': 'string'
            },
            'last_maintenance': {
                'value': '2025-01-15T10:30:00Z',
                'type': 'datetime'
            }
        }
    
    def _update_variables(self):
        """Actualizar valores de variables simuladas"""
        for var_name, var_config in self.variables.items():
            if var_config['type'] == 'float':
                current = var_config['value']
                variation = var_config.get('variation', 1.0)
                change = random.uniform(-variation, variation)
                new_value = current + change
                
                # Mantener dentro de los límites
                if 'min' in var_config:
                    new_value = max(new_value, var_config['min'])
                if 'max' in var_config:
                    new_value = min(new_value, var_config['max'])
                
                var_config['value'] = round(new_value, 2)
                
            elif var_config['type'] == 'integer':
                current = var_config['value']
                variation = var_config.get('variation', 1)
                change = random.randint(-variation, variation)
                new_value = current + change
                
                if 'min' in var_config:
                    new_value = max(new_value, var_config['min'])
                if 'max' in var_config:
                    new_value = min(new_value, var_config['max'])
                
                var_config['value'] = new_value
                
            elif var_config['type'] == 'boolean':
                # Cambiar estado ocasionalmente
                if random.random() < 0.1:  # 10% probabilidad
                    var_config['value'] = not var_config['value']
                    
            elif var_config['type'] == 'string' and 'options' in var_config:
                # Cambiar string ocasionalmente
                if random.random() < 0.05:  # 5% probabilidad
                    var_config['value'] = random.choice(var_config['options'])
    
    async def register_client(self, websocket):
        """Registrar nuevo cliente"""
        self.clients.add(websocket)
        logger.info(f"Cliente conectado: {websocket.remote_address}")
        
        # Enviar mensaje de bienvenida
        welcome_msg = {
            'type': 'welcome',
            'message': 'Conectado al servidor industrial WebSocket',
            'variables': list(self.variables.keys()),
            'timestamp': datetime.now().isoformat()
        }
        await websocket.send(json.dumps(welcome_msg))
    
    async def unregister_client(self, websocket):
        """Desregistrar cliente"""
        self.clients.discard(websocket)
        
        # Remover de suscripciones
        for address, subscribers in self.subscriptions.items():
            subscribers.discard(websocket)
        
        logger.info(f"Cliente desconectado: {websocket.remote_address}")
    
    async def handle_message(self, websocket, message):
        """Manejar mensaje recibido de cliente"""
        try:
            data = json.loads(message)
            action = data.get('action')
            address = data.get('address')
            
            if action == 'read':
                await self.handle_read(websocket, address)
            elif action == 'write':
                await self.handle_write(websocket, address, data.get('value'))
            elif action == 'subscribe':
                await self.handle_subscribe(websocket, address)
            elif action == 'unsubscribe':
                await self.handle_unsubscribe(websocket, address)
            elif action == 'list_variables':
                await self.handle_list_variables(websocket)
            else:
                await self.send_error(websocket, f"Acción no reconocida: {action}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Mensaje JSON inválido")
        except Exception as e:
            await self.send_error(websocket, f"Error procesando mensaje: {str(e)}")
    
    async def handle_read(self, websocket, address):
        """Manejar lectura de variable"""
        if address in self.variables:
            var_config = self.variables[address]
            response = {
                'type': 'read_response',
                'address': address,
                'value': var_config['value'],
                'unit': var_config.get('unit'),
                'data_type': var_config['type'],
                'timestamp': datetime.now().isoformat(),
                'quality': 'GOOD'
            }
            await websocket.send(json.dumps(response))
        else:
            await self.send_error(websocket, f"Variable no encontrada: {address}")
    
    async def handle_write(self, websocket, address, value):
        """Manejar escritura de variable"""
        if address in self.variables:
            var_config = self.variables[address]
            
            # Validar tipo de dato
            try:
                if var_config['type'] == 'float':
                    value = float(value)
                elif var_config['type'] == 'integer':
                    value = int(value)
                elif var_config['type'] == 'boolean':
                    value = bool(value)
                elif var_config['type'] == 'string':
                    value = str(value)
                
                # Actualizar valor
                var_config['value'] = value
                
                response = {
                    'type': 'write_response',
                    'address': address,
                    'value': value,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
                await websocket.send(json.dumps(response))
                
                # Notificar a suscriptores
                await self.notify_subscribers(address, value)
                
            except (ValueError, TypeError) as e:
                await self.send_error(websocket, f"Error de tipo de dato: {str(e)}")
        else:
            await self.send_error(websocket, f"Variable no encontrada: {address}")
    
    async def handle_subscribe(self, websocket, address):
        """Manejar suscripción a variable"""
        if address in self.variables:
            if address not in self.subscriptions:
                self.subscriptions[address] = set()
            
            self.subscriptions[address].add(websocket)
            
            response = {
                'type': 'subscribe_response',
                'address': address,
                'status': 'subscribed',
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(response))
            
            # Enviar valor actual
            var_config = self.variables[address]
            await self.notify_single_subscriber(websocket, address, var_config['value'])
            
        else:
            await self.send_error(websocket, f"Variable no encontrada: {address}")
    
    async def handle_unsubscribe(self, websocket, address):
        """Manejar cancelación de suscripción"""
        if address in self.subscriptions:
            self.subscriptions[address].discard(websocket)
            
            response = {
                'type': 'unsubscribe_response',
                'address': address,
                'status': 'unsubscribed',
                'timestamp': datetime.now().isoformat()
            }
            await websocket.send(json.dumps(response))
    
    async def handle_list_variables(self, websocket):
        """Enviar lista de variables disponibles"""
        variables_info = {}
        for name, config in self.variables.items():
            variables_info[name] = {
                'type': config['type'],
                'unit': config.get('unit'),
                'min': config.get('min'),
                'max': config.get('max'),
                'current_value': config['value']
            }
        
        response = {
            'type': 'variables_list',
            'variables': variables_info,
            'count': len(variables_info),
            'timestamp': datetime.now().isoformat()
        }
        await websocket.send(json.dumps(response))
    
    async def send_error(self, websocket, message):
        """Enviar mensaje de error"""
        error_msg = {
            'type': 'error',
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        await websocket.send(json.dumps(error_msg))
    
    async def notify_subscribers(self, address, value):
        """Notificar a todos los suscriptores de una variable"""
        if address in self.subscriptions:
            subscribers = self.subscriptions[address].copy()
            for websocket in subscribers:
                try:
                    await self.notify_single_subscriber(websocket, address, value)
                except websockets.exceptions.ConnectionClosed:
                    self.subscriptions[address].discard(websocket)
                except Exception as e:
                    logger.error(f"Error notificando suscriptor: {e}")
    
    async def notify_single_subscriber(self, websocket, address, value):
        """Notificar a un suscriptor específico"""
        var_config = self.variables[address]
        notification = {
            'type': 'data_update',
            'address': address,
            'value': value,
            'unit': var_config.get('unit'),
            'data_type': var_config['type'],
            'timestamp': datetime.now().isoformat(),
            'quality': 'GOOD'
        }
        await websocket.send(json.dumps(notification))
    
    async def periodic_update(self):
        """Actualizar variables periódicamente"""
        while self.running:
            self._update_variables()
            
            # Notificar cambios a suscriptores
            for address, config in self.variables.items():
                if address in self.subscriptions and self.subscriptions[address]:
                    await self.notify_subscribers(address, config['value'])
            
            await asyncio.sleep(2)  # Actualizar cada 2 segundos
    
    async def handle_client(self, websocket, path):
        """Manejar conexión de cliente"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Iniciar servidor WebSocket"""
        self.running = True
        
        # Iniciar tarea de actualización periódica
        update_task = asyncio.create_task(self.periodic_update())
        
        # Iniciar servidor WebSocket
        logger.info(f"Iniciando servidor WebSocket en {self.host}:{self.port}")
        
        try:
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info("Servidor WebSocket iniciado exitosamente")
                await asyncio.Future()  # Ejecutar indefinidamente
        except Exception as e:
            logger.error(f"Error en servidor WebSocket: {e}")
        finally:
            self.running = False
            update_task.cancel()


if __name__ == "__main__":
    # Crear y ejecutar servidor
    server = IndustrialWebSocketServer(host='localhost', port=8765)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error ejecutando servidor: {e}")
