# 🔄 Sistema Multi-Protocolo - Documentación

## 📋 Descripción General

El sistema SuperVisorioApp ha sido expandido para soportar múltiples protocolos de comunicación industrial, no solo OPC-UA. Ahora puedes conectarte a diferentes tipos de servidores y dispositivos usando:

- **OPC-UA** (Original)
- **OPC Classic** (DA/HDA)
- **WebSockets** (Tiempo real)
- **Modbus TCP** (En desarrollo)
- **MQTT** (En desarrollo)

## 🏗️ Arquitectura del Sistema

### Nuevos Modelos de Base de Datos

#### DataServer
```python
# Servidor de datos genérico que soporta múltiples protocolos
- name: Nombre del servidor
- server_type: Tipo (OPC_UA, OPC_CLASSIC, WEBSOCKET, MODBUS, MQTT)
- endpoint_url: URL/dirección de conexión
- connection_config: Configuración específica del protocolo (JSON)
- username/password: Credenciales de autenticación
```

#### DataVariable
```python
# Variable de datos genérica para cualquier protocolo
- server: Referencia al DataServer
- address: Dirección/NodeID/Tag de la variable
- data_type: Tipo de dato (BOOLEAN, INTEGER, FLOAT, STRING, DATETIME, JSON)
- protocol_config: Configuración específica del protocolo (JSON)
```

#### DataReading
```python
# Lectura de datos genérica con soporte para múltiples tipos
- variable: Referencia a DataVariable
- value_*: Campos para diferentes tipos de datos
- quality: Calidad del dato (GOOD, BAD, UNCERTAIN, TIMEOUT, ERROR)
- protocol_metadata: Metadatos específicos del protocolo (JSON)
```

### Cliente Multi-Protocolo

#### DataClientBase
Clase base abstracta que define la interfaz común para todos los clientes:
- `connect()`: Conectar al servidor
- `disconnect()`: Desconectar
- `read_variable()`: Leer una variable
- `write_variable()`: Escribir a una variable
- `subscribe_variable()`: Suscribirse a cambios

#### Clientes Específicos
- **OpcUaClient**: Cliente para servidores OPC-UA
- **WebSocketClient**: Cliente para comunicación WebSocket
- **OpcClassicClient**: Cliente para servidores OPC Classic (Windows)

#### DataManager
Administrador central que maneja múltiples clientes simultáneamente.

## 🚀 Uso del Sistema

### 1. Crear un Servidor de Datos

```python
# Ejemplo: Crear servidor WebSocket
server = DataServer.objects.create(
    name="Sistema SCADA Principal",
    server_type="WEBSOCKET",
    endpoint_url="ws://192.168.1.100:8765",
    connection_config={
        "protocol": "ws",
        "heartbeat_interval": 30,
        "reconnect_attempts": 5
    },
    created_by=user
)
```

### 2. Configurar Variables

```python
# Ejemplo: Variable de temperatura via WebSocket
variable = DataVariable.objects.create(
    server=server,
    address="temperature_reactor_1",
    name="Temperatura Reactor 1",
    data_type="FLOAT",
    unit="°C",
    is_monitored=True,
    sampling_interval=1000,
    protocol_config={
        "topic": "sensors/temperature/reactor1",
        "message_format": "json"
    },
    created_by=user
)
```

### 3. Conectar y Leer Datos

```python
from main_app.data_clients import data_manager

# Conectar al servidor
await data_manager.add_server(
    str(server.id),
    server.server_type,
    server.get_connection_config()
)

# Leer variable
value = await data_manager.read_variable(
    str(server.id),
    variable.address,
    variable.get_protocol_config()
)

# Escribir variable
success = await data_manager.write_variable(
    str(server.id),
    variable.address,
    25.5,
    variable.get_protocol_config()
)
```

## 🌐 API REST Endpoints

### Servidores de Datos
- `GET /api/data-servers/` - Listar servidores
- `POST /api/data-servers/` - Crear servidor
- `GET /api/data-servers/{id}/` - Obtener servidor
- `PUT /api/data-servers/{id}/` - Actualizar servidor
- `DELETE /api/data-servers/{id}/` - Eliminar servidor
- `POST /api/data-servers/{id}/connect/` - Conectar servidor
- `POST /api/data-servers/{id}/disconnect/` - Desconectar servidor
- `GET /api/data-servers/{id}/status/` - Estado del servidor
- `GET /api/data-servers/all_status/` - Estado de todos los servidores

### Variables de Datos
- `GET /api/data-variables/` - Listar variables
- `POST /api/data-variables/` - Crear variable
- `GET /api/data-variables/{id}/` - Obtener variable
- `PUT /api/data-variables/{id}/` - Actualizar variable
- `DELETE /api/data-variables/{id}/` - Eliminar variable
- `POST /api/data-variables/{id}/read_value/` - Leer valor actual
- `POST /api/data-variables/{id}/write_value/` - Escribir valor
- `POST /api/data-variables/{id}/subscribe/` - Suscribirse a variable
- `GET /api/data-variables/dashboard/` - Variables para dashboard

### Lecturas de Datos
- `GET /api/data-readings/` - Listar lecturas (filtros: variable, server, fechas)
- `GET /api/data-readings/latest/` - Últimas lecturas de todas las variables

### Utilidades
- `GET /api/protocols/supported/` - Protocolos soportados
- `POST /api/protocols/test-connection/` - Probar conexión
- `GET /api/dashboard/summary/` - Resumen del dashboard

## 🔧 Configuraciones por Protocolo

### OPC-UA
```json
{
  "security_mode": "NONE",
  "certificate_path": "",
  "private_key_path": ""
}
```

### WebSocket
```json
{
  "protocol": "ws",
  "heartbeat_interval": 30,
  "reconnect_attempts": 5
}
```

### OPC Classic
```json
{
  "clsid": "{...}",
  "prog_id": "OPC.Server.1",
  "update_rate": 1000
}
```

### Modbus TCP
```json
{
  "port": 502,
  "unit_id": 1,
  "timeout": 3
}
```

### MQTT
```json
{
  "port": 1883,
  "keep_alive": 60,
  "qos": 1
}
```

## 🧪 Servidor WebSocket de Ejemplo

El proyecto incluye un servidor WebSocket de ejemplo (`websocket_server_example.py`) que simula un sistema industrial con las siguientes variables:

- `temperature_1`: Temperatura (°C)
- `pressure_1`: Presión (hPa)
- `motor_1_status`: Estado del motor (boolean)
- `production_count`: Contador de producción
- `alarm_status`: Estado de alarmas
- `last_maintenance`: Última mantención

### Comandos Soportados
```json
// Leer variable
{"action": "read", "address": "temperature_1"}

// Escribir variable
{"action": "write", "address": "motor_1_status", "value": true}

// Suscribirse a variable
{"action": "subscribe", "address": "temperature_1"}

// Cancelar suscripción
{"action": "unsubscribe", "address": "temperature_1"}

// Listar variables
{"action": "list_variables"}
```

## 🔄 Migración desde OPC-UA

El sistema mantiene compatibilidad con los modelos existentes:
- `OpcUaServer` sigue funcionando
- `OpcUaVariable` sigue funcionando  
- `VariableReading` sigue funcionando

Los nuevos modelos (`DataServer`, `DataVariable`, `DataReading`) conviven con los anteriores.

## 📦 Dependencias Adicionales

```bash
# WebSockets
pip install websockets==14.1
pip install channels==4.1.0
pip install channels-redis==4.2.0

# Modbus
pip install pymodbus==3.7.4

# MQTT
pip install paho-mqtt==2.1.0

# Utilidades
pip install aiofiles==24.1.0
```

## 🧪 Pruebas

### Ejecutar Servidor WebSocket de Ejemplo
```bash
cd BackEnd/opcpr_project
python websocket_server_example.py
```

### Ejecutar Script de Pruebas
```bash
cd BackEnd
python test_multiprotocol.py
```

### Crear Datos de Prueba via Django Admin
1. Ir a `/admin/`
2. Crear un `DataServer` de tipo `WEBSOCKET`
3. Crear `DataVariable` asociadas
4. Usar las API para conectar y leer datos

## 📊 Dashboard Multi-Protocolo

El dashboard ahora muestra:
- Estado de conexión de múltiples tipos de servidores
- Variables de diferentes protocolos en una vista unificada
- Métricas por tipo de protocolo
- Alarmas de cualquier protocolo

## 🔒 Seguridad

- Autenticación requerida para todas las APIs
- Contraseñas encriptadas en la base de datos
- Validación de tipos de datos
- Logs de auditoría para todas las operaciones

## 🎯 Próximos Pasos

1. ✅ **Completado**: Modelos base y clientes OPC-UA/WebSocket
2. 🔄 **En desarrollo**: Clientes Modbus y MQTT
3. 📋 **Planeado**: Interfaz web para configuración
4. 📋 **Planeado**: Dashboards tiempo real con WebSockets
5. 📋 **Planeado**: Sistema de alarmas unificado
6. 📋 **Planeado**: Reportes históricos multi-protocolo

---

**¡El sistema ahora es verdaderamente multi-protocolo! 🎉**
