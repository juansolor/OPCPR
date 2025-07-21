# 📋 Changelog

Todos los cambios importantes en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere al [Versionado Semántico](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🔄 En Desarrollo
- Conexión a servidores OPC-UA reales
- WebSockets para datos en tiempo real
- Sistema de notificaciones push
- Gráficos avanzados con Chart.js

## [1.0.0] - 2025-07-21

### ✨ Añadido
- **Sistema de Autenticación Completo**
  - Registro de usuarios con validación
  - Login con tokens JWT
  - Perfiles de usuario con niveles de acceso
  - Protección automática de rutas

- **Base de Datos SQLite3**
  - 9 modelos personalizados para supervisión industrial
  - Sistema de migraciones Django
  - Datos iniciales preconfigurados
  - Panel de administración integrado

- **API REST con Axios**
  - Cliente HTTP configurado con interceptores
  - Manejo automático de tokens de autenticación
  - Manejo global de errores HTTP
  - Servicios tipados con TypeScript

- **Interfaz de Usuario Completa**
  - Dashboard principal con navegación
  - Página de variables analógicas con datos simulados
  - Monitoreo de entradas/salidas digitales
  - Estado de conexiones en tiempo real
  - Diseño responsive y profesional

- **Arquitectura Moderna**
  - Frontend: React Router v7 + TypeScript + Vite
  - Backend: Django 5.2 + DRF + SQLite3
  - Separación clara frontend/backend
  - Configuración de desarrollo lista

### 🔧 Técnico
- **Modelos de Base de Datos**
  - `OpcUaServer`: Configuración de servidores OPC-UA
  - `OpcUaVariable`: Variables monitoreadas con alarmas
  - `VariableReading`: Historial de lecturas
  - `Alarm`: Sistema completo de alarmas industriales
  - `ConnectionLog`: Logs de conectividad
  - `UserProfile`: Perfiles extendidos de usuario
  - `SystemConfiguration`: Configuraciones del sistema
  - `AuditLog`: Registro de auditoría

- **API Endpoints**
  - `/api/auth/` - Autenticación (register, login, logout)
  - `/api/opcua/` - Datos OPC-UA (servers, variables, readings, alarms)
  - `/api/system/` - Configuraciones del sistema

- **Características de Seguridad**
  - Autenticación basada en tokens
  - Validación de entrada en frontend y backend
  - Protección CORS configurada
  - Sanitización de datos

### 🎨 Interfaz
- **Páginas Implementadas**
  - Home: Página de bienvenida con información del proyecto
  - Login: Autenticación con validación de formularios
  - Register: Registro de usuarios con confirmación
  - Dashboard: Vista principal con tarjetas de navegación
  - Variables Analógicas: Monitoreo con datos simulados
  - E/S Digitales: Estado de contactos y actuadores
  - Estado de Conexión: Métricas del sistema y conectividad

- **Características de UX**
  - Diseño industrial profesional
  - Iconografía intuitiva
  - Feedback visual para acciones
  - Actualización automática de datos
  - Navegación fluida entre módulos

### 📦 Dependencias Principales
- **Frontend**
  - React Router v7
  - TypeScript 5.0+
  - Axios para peticiones HTTP
  - Vite como build tool
  - CSS Modules para estilos

- **Backend**
  - Django 5.2
  - Django REST Framework
  - Django CORS Headers
  - SQLite3 (incluido con Python)

### 🚀 Deploy y Configuración
- Scripts de configuración automatizada
- Migraciones de base de datos
- Datos iniciales preconfigurados
- Documentación completa de instalación
- Variables de entorno configurables

---

## [0.1.0] - 2025-07-20

### ✨ Proyecto Inicial
- Configuración inicial del repositorio
- Estructura básica de carpetas
- Configuración de entornos de desarrollo

---

### Tipos de Cambios
- **✨ Añadido** para nuevas funcionalidades
- **🔧 Cambiado** para cambios en funcionalidades existentes
- **❌ Obsoleto** para funcionalidades que se eliminarán
- **🗑️ Eliminado** para funcionalidades eliminadas
- **🐛 Arreglado** para corrección de bugs
- **🔒 Seguridad** para vulnerabilidades
