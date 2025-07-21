# OPCPR Django Backend

Este es el backend del proyecto OPCPR desarrollado en Django con API REST para supervisorio OPC UA.

## Requisitos

- Python 3.11+
- Django 5.2.4
- PostgreSQL (opcional, por defecto usa SQLite)

## Instalación Rápida

1. **Activar el ambiente virtual** (ya está configurado):
```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

2. **Instalar dependencias adicionales** (si es necesario):
```bash
pip install requests opcua
```

3. **Ejecutar migraciones** (ya ejecutadas):
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Crear superusuario** (opcional):
```bash
python manage.py createsuperuser
```

5. **Iniciar el servidor**:
```bash
# Opción 1: Comando directo
python manage.py runserver

# Opción 2: Script de Windows
start_server.bat
```

6. **Probar la API**:
```bash
# Ejecutar tests automatizados
python manage.py test

# Ejecutar script de pruebas de la API
python test_api.py
```

## 🚀 **API del Supervisorio OPC UA**

### Endpoints Disponibles:

1. **Health Check**: `GET /api/health/`
2. **Supervisorio OPC UA**: 
   - `GET /api/supervisorio/?url=opc.tcp://localhost:4840`
   - `POST /api/supervisorio/`

### Ejemplos de Uso:

**Leer datos del supervisorio:**
```bash
curl -X GET "http://localhost:8000/api/supervisorio/?url=opc.tcp://localhost:4840"
```

**Escribir datos al supervisorio:**
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

## 📁 **Estructura del Proyecto**

```
BackEnd/
├── opcpr_project/          # Configuración principal de Django
│   ├── settings.py        # Configuraciones del proyecto
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # Configuración WSGI
├── main_app/              # Aplicación principal
│   ├── models.py         # Modelos de base de datos
│   ├── views.py          # Vistas y lógica de negocio (API OPC UA)
│   ├── opcua_client.py   # Cliente OPC UA personalizado
│   ├── serializers.py    # Serializers para API REST
│   ├── urls.py           # URLs de la aplicación
│   ├── admin.py          # Configuración del admin
│   └── tests.py          # Tests automatizados
├── templates/             # Templates HTML
├── static/               # Archivos estáticos
├── media/                # Archivos subidos
├── .env                  # Variables de entorno
├── start_server.bat      # Script para iniciar servidor (Windows)
├── test_api.py          # Script de pruebas de la API
├── API_DOCUMENTATION.md  # Documentación detallada de la API
└── manage.py            # Comando principal
```

## 🧪 **Testing**

### Tests Automatizados:
```bash
python manage.py test
```

### Script de Pruebas de la API:
```bash
python test_api.py
```

### Tests Manuales:
- Visitar `http://localhost:8000` para la interfaz web
- Visitar `http://localhost:8000/api/health/` para verificar la API
- Visitar `http://localhost:8000/api/supervisorio/` para el supervisorio OPC UA

## 🔧 **Características Implementadas**

- ✅ **API GET**: Lee datos del servidor OPC UA
- ✅ **API POST**: Escribe datos al servidor OPC UA  
- ✅ **Datos simulados**: Si no hay servidor OPC UA, usa datos simulados
- ✅ **Validaciones**: Validación de datos de entrada
- ✅ **Manejo de errores**: Respuestas HTTP apropiadas
- ✅ **Tests automatizados**: 7 tests que cubren todos los casos
- ✅ **Documentación**: Documentación completa de la API
- ✅ **CORS habilitado**: Para conexiones desde frontend

## 🌐 **URLs de Acceso**

- **Interfaz principal**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin/
- **API Health**: http://localhost:8000/api/health/
- **API Supervisorio**: http://localhost:8000/api/supervisorio/

## 📋 **Comandos Útiles**

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver

# Ejecutar tests
python manage.py test

# Recopilar archivos estáticos
python manage.py collectstatic

# Instalar nuevas dependencias
pip install [package]
pip freeze > requirements.txt
```

## 🚨 **Errores Solucionados**

- ✅ **ImportError corregido**: Eliminadas importaciones incorrectas en urls.py
- ✅ **Cryptography instalada**: Eliminados los warnings de crypto
- ✅ **URLs duplicadas**: Limpiadas las rutas duplicadas
- ✅ **Servidor funcionando**: Django corriendo correctamente en puerto 8000
- ✅ **API probada**: Todos los endpoints funcionan con datos simulados

## 🚨 **Notas Importantes**

- Los datos simulados se usan cuando no hay servidor OPC UA disponible
- La API está configurada con permisos abiertos para desarrollo
- Para producción, configurar autenticación y HTTPS
- Los tests pueden mostrar warnings de OPC UA, esto es normal
- El servidor debe estar corriendo para usar el script de pruebas
