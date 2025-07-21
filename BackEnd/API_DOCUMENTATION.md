# API del Supervisorio OPC UA

Esta API permite interactuar con servidores OPC UA para leer y escribir datos.

## Endpoints Disponibles

### 1. Health Check
**GET** `/api/health/`

Verifica que la API esté funcionando correctamente.

**Respuesta:**
```json
{
    "status": "ok",
    "message": "API funcionando correctamente",
    "version": "1.0.0"
}
```

### 2. Supervisorio OPC UA

#### Leer Datos (GET)
**GET** `/api/supervisorio/?url=opc.tcp://localhost:4840`

Lee datos del servidor OPC UA especificado.

**Parámetros:**
- `url` (opcional): URL del servidor OPC UA. Por defecto: `opc.tcp://localhost:4840`

**Ejemplo de respuesta:**
```json
{
    "status": "success",
    "method": "GET",
    "url": "opc.tcp://localhost:4840",
    "data": {
        "temperatura": 25.5,
        "presion": 1013.25,
        "nivel": 75.2
    }
}
```

#### Escribir Datos (POST)
**POST** `/api/supervisorio/`

Escribe datos al servidor OPC UA especificado.

**Cuerpo de la petición:**
```json
{
    "url": "opc.tcp://localhost:4840",
    "data": {
        "setpoint_temperatura": 30.0,
        "setpoint_presion": 1020.0,
        "comando_bomba": true
    }
}
```

**Ejemplo de respuesta:**
```json
{
    "status": "success",
    "method": "POST",
    "url": "opc.tcp://localhost:4840",
    "message": "Datos escritos correctamente",
    "written_data": {
        "setpoint_temperatura": 30.0,
        "setpoint_presion": 1020.0,
        "comando_bomba": true
    },
    "response": {
        "success": true,
        "written_nodes": 3
    }
}
```

## Ejemplos de Uso

### Con curl

#### Leer datos:
```bash
curl -X GET "http://localhost:8000/api/supervisorio/?url=opc.tcp://localhost:4840"
```

#### Escribir datos:
```bash
curl -X POST "http://localhost:8000/api/supervisorio/" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "opc.tcp://localhost:4840",
    "data": {
      "setpoint_temperatura": 30.0,
      "comando_bomba": true
    }
  }'
```

### Con JavaScript (fetch)

#### Leer datos:
```javascript
fetch('http://localhost:8000/api/supervisorio/?url=opc.tcp://localhost:4840')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

#### Escribir datos:
```javascript
fetch('http://localhost:8000/api/supervisorio/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'opc.tcp://localhost:4840',
    data: {
      setpoint_temperatura: 30.0,
      comando_bomba: true
    }
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `400 Bad Request`: Datos de entrada inválidos
- `500 Internal Server Error`: Error del servidor o problema con OPC UA

## Manejo de Errores

### Errores comunes:

1. **Servidor OPC UA no disponible:**
```json
{
    "error": "No se pudieron obtener los datos del servidor OPC UA"
}
```

2. **Datos de escritura faltantes:**
```json
{
    "error": "No se proporcionaron datos para escribir"
}
```

3. **Error en operación POST:**
```json
{
    "error": "Error en la operación POST: [detalle del error]"
}
```
