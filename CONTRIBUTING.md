# 🤝 Contribuir al Proyecto SuperVisorioApp

¡Gracias por tu interés en contribuir al proyecto! Tu ayuda es muy valiosa para mejorar este sistema de supervisión OPC-UA.

## 📋 Formas de Contribuir

### 🐛 Reportar Bugs
- Usa las [GitHub Issues](https://github.com/juansolor/OPCPR/issues)
- Incluye pasos para reproducir el problema
- Adjunta screenshots si es relevante
- Especifica el entorno (OS, versión de Python/Node, etc.)

### ✨ Sugerir Funcionalidades
- Abre una issue con la etiqueta "enhancement"
- Describe el caso de uso
- Explica el valor que agregaría al proyecto

### 🔧 Enviar Código
- Fork del repositorio
- Crear rama descriptiva (`feature/nueva-funcionalidad`)
- Seguir estándares de código
- Incluir tests si es aplicable
- Documentar cambios en commits

## 🏗️ Configuración del Entorno de Desarrollo

### Backend (Django)
```bash
cd BackEnd
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Herramientas de desarrollo
```

### Frontend (React)
```bash
cd FrontEnd/SuperVisorioApp
npm install
npm run dev
```

## 📝 Estándares de Código

### Python/Django
- **Black** para formateo automático
- **isort** para organización de imports
- **flake8** para linting
- **mypy** para type checking

```bash
# Formatear código
black .
isort .

# Verificar calidad
flake8 .
mypy .
```

### TypeScript/React
- **Prettier** para formateo
- **ESLint** para linting
- **TypeScript strict mode** habilitado

```bash
# Formatear y verificar
npm run format
npm run lint
npm run type-check
```

## 🧪 Testing

### Backend Tests
```bash
python manage.py test
coverage run --source='.' manage.py test
coverage report
```

### Frontend Tests
```bash
npm run test
npm run test:coverage
```

## 📊 Estructura de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: agregar autenticación de dos factores
fix: corregir error en conexión OPC-UA
docs: actualizar guía de instalación
style: formatear código con prettier
refactor: reestructurar servicios de API
test: agregar tests para modelos de alarmas
chore: actualizar dependencias
```

## 🔍 Pull Request Process

1. **Fork** del repositorio
2. **Crear rama** descriptiva
3. **Desarrollar** funcionalidad
4. **Escribir tests** (si aplica)
5. **Actualizar documentación**
6. **Commit** con mensaje descriptivo
7. **Push** a tu fork
8. **Crear PR** con descripción detallada

### Template de PR
```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix
- [ ] Nueva funcionalidad
- [ ] Breaking change
- [ ] Actualización de documentación

## Testing
- [ ] Tests pasan localmente
- [ ] Agregué nuevos tests si es necesario

## Checklist
- [ ] Mi código sigue los estándares del proyecto
- [ ] He revisado mi propio código
- [ ] He actualizado la documentación
```

## 🎯 Áreas de Contribución Prioritarias

### 🔥 Alto Impacto
- **Conexión OPC-UA real** (no simulada)
- **WebSockets** para tiempo real
- **Tests automatizados** completos
- **Documentación de API** con Swagger

### 🌟 Funcionalidades Nuevas
- **Gráficos avanzados** para tendencias
- **Sistema de notificaciones** push
- **Exportación de datos** (Excel, PDF, CSV)
- **Dashboard personalizable**

### 🛠️ Mejoras Técnicas
- **Performance optimization**
- **Security hardening**
- **Error handling** mejorado
- **Accessibility** (a11y)

## 📚 Recursos Útiles

### Documentación Técnica
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Router](https://reactrouter.com/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [OPC-UA Specification](https://opcfoundation.org/)

### Herramientas de Desarrollo
- [VS Code Extensions](./docs/vscode-extensions.md)
- [Postman Collection](./docs/postman-collection.json)
- [Database Schema](./docs/database-schema.md)

## 🏆 Reconocimientos

### Contribuidores Principales
- **Juan Solor** - Creador y mantenedor principal
- **Tu nombre aquí** - ¡Sé el próximo contribuidor!

### Hall of Fame
Los mejores contribuidores serán reconocidos aquí con sus PRs más significativos.

## 💬 Comunicación

### Canales de Comunicación
- **Issues**: Para bugs y feature requests
- **Discussions**: Para preguntas generales
- **Email**: juansolor@email.com (para temas sensibles)

### Tiempo de Respuesta
- **Issues críticos**: 24-48 horas
- **PRs**: 3-5 días laborales
- **Feature requests**: 1-2 semanas

## 🎉 ¡Empezar es Fácil!

### Issues para Principiantes
Busca issues con las etiquetas:
- `good first issue`
- `help wanted`
- `beginner friendly`

### Quick Wins
- Corregir typos en documentación
- Agregar tests unitarios
- Mejorar mensajes de error
- Optimizar consultas de base de datos

---

**¡Gracias por contribuir al futuro de la supervisión industrial! 🚀**
