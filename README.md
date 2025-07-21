# 🏭 SuperVisorioApp - Sistema de Supervisión OPC-UA

[![React](https://img.shields.io/badge/React-18.0-blue)](https://reactjs.org/)
[![Django](https://img.shields.io/badge/Django-5.2-green)](https://djangoproject.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11-yellow)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-red)](LICENSE)

## 📋 Descripción

**SuperVisorioApp** es un sistema completo de supervisión industrial basado en el protocolo **OPC-UA**, diseñado para monitorear y controlar variables analógicas, entradas/salidas digitales, y gestionar alarmas en tiempo real.

El proyecto está construido con una arquitectura moderna de **frontend-backend** separados, utilizando React Router v7 con TypeScript para el cliente y Django REST Framework para el servidor.

## ✨ Características Principales

### 🔐 **Sistema de Autenticación**
- Registro y login de usuarios con validación completa
- Autenticación basada en tokens JWT
- Perfiles de usuario con niveles de acceso (Viewer, Operator, Supervisor, Admin)
- Protección de rutas automática

### 📊 **Monitoreo Industrial**
- **Variables Analógicas**: Monitoreo en tiempo real con gráficos y tendencias
- **Entradas/Salidas Digitales**: Estado de contactos, relés y actuadores
- **Estado de Conexión**: Supervisión de servidores OPC-UA y métricas del sistema
- **Sistema de Alarmas**: Gestión completa con reconocimiento y histórico

### 🌐 **Conectividad OPC-UA**
- Conexión a múltiples servidores OPC-UA
- Configuración de seguridad personalizable
- Monitoreo de estado de conexiones en tiempo real
- Logs de conectividad y errores

### 📈 **Dashboard Ejecutivo**
- Vista general del sistema con métricas clave
- Navegación intuitiva entre módulos
- Indicadores de estado en tiempo real
- Resumen de alarmas activas

## 🏗️ Arquitectura del Sistema

```
SuperVisorioApp/
├── 🎨 FrontEnd/                 # React Router v7 + TypeScript
│   ├── app/routes/              # Páginas de la aplicación
│   ├── app/services/            # APIs y servicios HTTP
│   ├── app/types/               # Tipos TypeScript
│   ├── app/utils/               # Utilidades de autenticación
│   └── app/styles/              # Estilos CSS modulares
│
├── ⚙️ BackEnd/                  # Django REST Framework
│   ├── main_app/                # Aplicación principal
│   │   ├── models.py            # Modelos de base de datos
│   │   ├── views.py             # API endpoints
│   │   ├── serializers.py       # Serialización de datos
│   │   └── admin.py             # Panel de administración
│   ├── opcpr_project/           # Configuración del proyecto
│   └── db.sqlite3               # Base de datos SQLite3
│
└── 📚 Documentation/            # Documentación del proyecto
```

## 🚀 Tecnologías Utilizadas

### Frontend
- **React Router v7** - Enrutamiento moderno con soporte SSR
- **TypeScript** - Tipado estático para mejor desarrollo
- **Axios** - Cliente HTTP con interceptores y manejo de errores
- **CSS Modules** - Estilos modulares y reutilizables
- **Vite** - Build tool rápido y moderno

### Backend
- **Django 5.2** - Framework web robusto y escalable
- **Django REST Framework** - API REST completa
- **SQLite3** - Base de datos ligera y eficiente
- **Token Authentication** - Autenticación segura
- **CORS** - Soporte para peticiones cross-origin

### Base de Datos
- **9 Modelos personalizados** para el dominio industrial
- **Relaciones complejas** entre entidades
- **Índices optimizados** para consultas rápidas
- **Sistema de migración** versionado

## 📦 Instalación y Configuración

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/juansolor/OPCPR.git
cd OPCPR
```

### 2. Configurar Backend (Django)
```bash
cd BackEnd

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# Cargar datos iniciales
python manage.py loaddata initial_data.json

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### 3. Configurar Frontend (React)
```bash
cd ../FrontEnd/SuperVisorioApp

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

### 4. Acceder al Sistema
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api
- **Admin Panel**: http://localhost:8000/admin

## 🔧 Configuración de API

El sistema incluye configuración avanzada de Axios con:

```typescript
// Interceptores automáticos
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Manejo de errores globales
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirigir a login automáticamente
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 📊 Modelos de Base de Datos

### Principales Entidades
- **OpcUaServer**: Configuración de servidores OPC-UA
- **OpcUaVariable**: Variables monitoreadas con configuración de alarmas
- **VariableReading**: Lecturas históricas con timestamps
- **Alarm**: Sistema completo de alarmas industriales
- **ConnectionLog**: Logs de conectividad y errores
- **UserProfile**: Perfiles extendidos de usuario
- **SystemConfiguration**: Configuraciones del sistema

### Relaciones Clave
```sql
-- Ejemplo de relaciones
OpcUaServer (1) → (N) OpcUaVariable
OpcUaVariable (1) → (N) VariableReading  
OpcUaVariable (1) → (N) Alarm
User (1) → (1) UserProfile
```

## 🔌 API Endpoints

### Autenticación
```
POST /api/auth/register/     - Registro de usuario
POST /api/auth/login/        - Inicio de sesión
POST /api/auth/logout/       - Cierre de sesión
```

### OPC-UA
```
GET  /api/opcua/servers/                    - Lista de servidores
GET  /api/opcua/variables/                  - Variables monitoreadas
GET  /api/opcua/variables/{id}/readings/    - Lecturas de variable
GET  /api/opcua/connection-status/          - Estado de conexiones
GET  /api/opcua/alarms/                     - Alarmas del sistema
POST /api/opcua/alarms/{id}/acknowledge/    - Reconocer alarma
```

### Sistema
```
GET  /api/system/configurations/     - Configuraciones del sistema
PUT  /api/system/configurations/{key}/  - Actualizar configuración
```

## 🎨 Interfaz de Usuario

### Páginas Principales
1. **🏠 Home** - Página de bienvenida con información del sistema
2. **🔐 Login/Register** - Autenticación de usuarios
3. **📊 Dashboard** - Vista general con navegación a módulos
4. **📈 Variables Analógicas** - Monitoreo de valores continuos
5. **🔌 Entradas/Salidas Digitales** - Estado de contactos ON/OFF
6. **🌐 Estado de Conexión** - Supervisión de conectividad

### Características de UI/UX
- **Diseño responsive** para desktop y mobile
- **Tema industrial** con colores profesionales
- **Iconografía intuitiva** para fácil navegación
- **Feedback visual** para acciones del usuario
- **Actualización en tiempo real** de datos críticos

## 🔒 Seguridad

### Medidas Implementadas
- **Autenticación basada en tokens** con expiración
- **Protección CORS** configurada
- **Validación de entrada** en frontend y backend
- **Sanitización de datos** para prevenir XSS
- **Manejo seguro de contraseñas** con hashing
- **Logs de auditoría** para trazabilidad

## 📈 Monitoreo y Logs

### Sistema de Auditoría
- **AuditLog**: Registro de todas las acciones del usuario
- **ConnectionLog**: Historial de conexiones y errores
- **Error Tracking**: Captura y logging de errores
- **Performance Metrics**: Métricas de rendimiento del sistema

## 🤝 Contribución

### Flujo de Desarrollo
1. Fork del proyecto
2. Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

### Estándares de Código
- **ESLint + Prettier** para JavaScript/TypeScript
- **Black + isort** para Python
- **Conventional Commits** para mensajes
- **Tests unitarios** obligatorios para nuevas funcionalidades

## 📋 Roadmap

### 🚧 Próximas Funcionalidades
- [ ] **WebSockets** para datos en tiempo real
- [ ] **Gráficos avanzados** con Chart.js/D3.js
- [ ] **Notificaciones push** para alarmas críticas
- [ ] **Exportación de datos** a Excel/PDF
- [ ] **API REST documentada** con Swagger/OpenAPI
- [ ] **Tests automatizados** con Jest + Pytest
- [ ] **Docker containerization** para deployment
- [ ] **CI/CD pipeline** con GitHub Actions

### 🎯 Funcionalidades Futuras
- [ ] **Multiples bases de datos** (PostgreSQL, InfluxDB)
- [ ] **Clustering** de servidores OPC-UA
- [ ] **Machine Learning** para predicción de fallos
- [ ] **Mobile App** nativa con React Native
- [ ] **Integración IoT** con MQTT y otros protocolos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Equipo de Desarrollo

- **[Juan Solor](https://github.com/juansolor)** - Desarrollador Principal
- **Contribuidores** - ¡Tu nombre podría estar aquí!

## 🆘 Soporte

### Reportar Problemas
- **Issues**: [GitHub Issues](https://github.com/juansolor/OPCPR/issues)
- **Discussions**: [GitHub Discussions](https://github.com/juansolor/OPCPR/discussions)

### Documentación Adicional
- [📚 Documentación Técnica](./docs/)
- [🔧 Guía de Instalación](./docs/installation.md)
- [📋 API Reference](./docs/api.md)
- [🎨 Guía de UI/UX](./docs/design.md)

---

<div align="center">

**⭐ Si este proyecto te resulta útil, ¡dale una estrella en GitHub! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/juansolor/OPCPR.svg?style=social&label=Star)](https://github.com/juansolor/OPCPR)
[![GitHub forks](https://img.shields.io/github/forks/juansolor/OPCPR.svg?style=social&label=Fork)](https://github.com/juansolor/OPCPR/fork)

</div>
