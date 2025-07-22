# 🚀 Comandos Útiles - Sistema Multi-Protocolo

## 📦 Instalación y Configuración

### Instalar dependencias adicionales
```bash
cd BackEnd
pip install websockets==14.1 channels==4.1.0 pymodbus==3.7.4 paho-mqtt==2.1.0
```

### Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### Crear superusuario (si no existe)
```bash
python manage.py createsuperuser
```

## 🧪 Pruebas y Demos

### Iniciar servidor WebSocket de ejemplo
```bash
cd BackEnd/opcpr_project
python websocket_server_example.py
```

### Ejecutar pruebas multi-protocolo
```bash
cd BackEnd  
python test_multiprotocol.py
```

### Iniciar servidor Django
```bash
cd BackEnd
python manage.py runserver
```

## 🌐 URLs Importantes

- **Panel Admin**: http://localhost:8000/admin/
- **API Root**: http://localhost:8000/api/
- **Health Check**: http://localhost:8000/api/health/
- **Protocolos Soportados**: http://localhost:8000/api/protocols/supported/
- **Dashboard Summary**: http://localhost:8000/api/dashboard/summary/

## 📊 APIs Multi-Protocolo

### Servidores de Datos
```bash
# Listar servidores
GET http://localhost:8000/api/data-servers/

# Crear servidor WebSocket
POST http://localhost:8000/api/data-servers/
{
  "name": "Test WebSocket",
  "server_type": "WEBSOCKET", 
  "endpoint_url": "ws://localhost:8765",
  "is_active": true
}

# Conectar servidor
POST http://localhost:8000/api/data-servers/1/connect/

# Estado de conexión
GET http://localhost:8000/api/data-servers/1/status/
```

### Variables de Datos
```bash
# Crear variable
POST http://localhost:8000/api/data-variables/
{
  "server": 1,
  "address": "temperature_1",
  "name": "Temperatura 1",
  "data_type": "FLOAT",
  "variable_type": 1,
  "is_monitored": true
}

# Leer valor actual
POST http://localhost:8000/api/data-variables/1/read_value/

# Escribir valor
POST http://localhost:8000/api/data-variables/1/write_value/
{
  "value": 25.5
}

# Suscribirse a variable
POST http://localhost:8000/api/data-variables/1/subscribe/
```

### Lecturas de Datos
```bash
# Últimas lecturas
GET http://localhost:8000/api/data-readings/latest/

# Lecturas de una variable
GET http://localhost:8000/api/data-readings/?variable=1

# Lecturas por fechas
GET http://localhost:8000/api/data-readings/?start_date=2025-01-01&end_date=2025-12-31
```

## 🔧 Comandos de Desarrollo

### Hacer migraciones específicas
```bash
python manage.py makemigrations main_app
```

### Resetear migraciones (¡Cuidado!)
```bash
python manage.py migrate main_app zero
python manage.py migrate main_app
```

### Cargar datos iniciales
```bash
python manage.py loaddata main_app/fixtures/initial_data.json
```

### Crear datos de prueba
```bash
python manage.py shell
```
```python
from main_app.models import DataServer, DataVariable, VariableType

# Crear tipo de variable
var_type = VariableType.objects.create(name="Sensor")

# Crear servidor WebSocket
server = DataServer.objects.create(
    name="Test WebSocket",
    server_type="WEBSOCKET",
    endpoint_url="ws://localhost:8765",
    created_by_id=1
)

# Crear variables
DataVariable.objects.create(
    server=server,
    address="temperature_1",
    name="Temperatura 1",
    data_type="FLOAT",
    variable_type=var_type,
    created_by_id=1
)
```

## 📁 Archivos Importantes

### Backend
- `main_app/models.py` - Modelos de datos multi-protocolo
- `main_app/data_clients.py` - Clientes para protocolos
- `main_app/data_views.py` - APIs REST multi-protocolo
- `main_app/serializers.py` - Serializers expandidos
- `test_multiprotocol.py` - Script de pruebas

### Documentación
- `MULTIPROTOCOL_DOCUMENTATION.md` - Documentación técnica
- `MULTIPROTOCOL_README.md` - Guía del usuario
- `PROJECT_OVERVIEW.md` - Resumen del proyecto

### Demos
- `opcpr_project/websocket_server_example.py` - Servidor WebSocket
- `setup_multiprotocol.bat` - Script de configuración
- `demo_websocket.bat` - Demo WebSocket

## 🧪 Ejemplos de Configuración

### Servidor OPC-UA
```json
{
  "name": "PLC Siemens",
  "server_type": "OPC_UA", 
  "endpoint_url": "opc.tcp://192.168.1.100:4840",
  "connection_config": {
    "security_mode": "NONE"
  }
}
```

### Servidor WebSocket
```json
{
  "name": "SCADA Web",
  "server_type": "WEBSOCKET",
  "endpoint_url": "ws://192.168.1.200:8765", 
  "connection_config": {
    "heartbeat_interval": 30,
    "reconnect_attempts": 5
  }
}
```

### Servidor Modbus
```json
{
  "name": "Dispositivo Modbus",
  "server_type": "MODBUS",
  "endpoint_url": "192.168.1.50",
  "connection_config": {
    "port": 502,
    "unit_id": 1,
    "timeout": 3
  }
}
```

## 🔍 Debugging

### Ver logs del servidor
```bash
python manage.py runserver --verbosity=2
```

### Activar logging detallado
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Probar conexión sin guardar
```bash
POST http://localhost:8000/api/protocols/test-connection/
{
  "server_type": "WEBSOCKET",
  "endpoint_url": "ws://localhost:8765"
}
```

---

**💡 Tip**: Mantén este archivo como referencia rápida para trabajar con el sistema multi-protocolo.
