# 🚀 Comandos de Desarrollo Rápido

Este archivo contiene comandos útiles para trabajar con el proyecto SuperVisorioApp.

## 📦 Instalación Inicial

### Backend (Django)
```bash
cd BackEnd
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_data.json
python manage.py createsuperuser
```

### Frontend (React)
```bash
cd FrontEnd/SuperVisorioApp
npm install
```

## 🔧 Comandos de Desarrollo

### Backend
```bash
# Servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Shell interactivo de Django
python manage.py shell

# Cargar datos de prueba
python manage.py loaddata fixtures/sample_data.json

# Crear superusuario
python manage.py createsuperuser

# Verificar problemas
python manage.py check

# Ejecutar tests
python manage.py test

# Limpiar migraciones (CUIDADO)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
```

### Frontend
```bash
# Servidor de desarrollo
npm run dev

# Build de producción
npm run build

# Preview del build
npm run preview

# Linting
npm run lint

# Formateo
npm run format

# Type checking
npm run type-check

# Instalar dependencia
npm install <package-name>

# Instalar dev dependency
npm install -D <package-name>

# Actualizar dependencias
npm update

# Auditoría de seguridad
npm audit
npm audit fix
```

## 🗄️ Comandos de Base de Datos

### SQLite3 Commands
```bash
# Conectar a la base de datos
sqlite3 db.sqlite3

# Mostrar tablas
.tables

# Describe tabla
.schema table_name

# Mostrar datos de tabla
SELECT * FROM table_name;

# Backup de base de datos
.backup backup.db

# Restaurar backup
.restore backup.db

# Salir
.quit
```

### Django Database Commands
```bash
# Reset completo de base de datos (DESTRUCTIVO)
rm db.sqlite3
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata initial_data.json

# Dump de datos
python manage.py dumpdata > data.json
python manage.py dumpdata main_app > main_app_data.json

# Mostrar migraciones
python manage.py showmigrations

# Revertir migración
python manage.py migrate main_app 0001
```

## 🔍 Debugging y Logs

### Backend Debugging
```bash
# Logs detallados de Django
python manage.py runserver --verbosity=2

# Debug con pdb
import pdb; pdb.set_trace()

# Verificar configuración
python manage.py diffsettings

# Mostrar URLs
python manage.py show_urls
```

### Frontend Debugging
```bash
# Dev tools con source maps
npm run dev

# Análisis del bundle
npm run build -- --analyze

# Logs detallados
DEBUG=* npm run dev
```

## 🧪 Testing

### Backend Tests
```bash
# Ejecutar todos los tests
python manage.py test

# Test específico
python manage.py test main_app.tests.TestModelName

# Coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Frontend Tests (cuando estén configurados)
```bash
# Ejecutar tests
npm test

# Tests con coverage
npm run test:coverage

# Tests en modo watch
npm run test:watch
```

## 📋 Comandos de Producción

### Backend Production
```bash
# Collectstatic para archivos estáticos
python manage.py collectstatic

# Verificar deployment
python manage.py check --deploy

# Crear fixtures de producción
python manage.py dumpdata --natural-foreign --natural-primary > prod_data.json
```

### Frontend Production
```bash
# Build optimizado
npm run build

# Servir build local
npm run preview

# Análisis del bundle
npm run build -- --analyze
```

## 🔧 Utilidades de Git

### Comandos Útiles
```bash
# Status completo
git status

# Agregar todos los cambios
git add .

# Commit con mensaje
git commit -m "feat: agregar nueva funcionalidad"

# Push de rama actual
git push origin $(git branch --show-current)

# Crear y cambiar a nueva rama
git checkout -b feature/nueva-funcionalidad

# Actualizar desde main
git pull origin main

# Merge de main a rama actual
git merge main

# Ver logs bonitos
git log --oneline --graph --decorate
```

## 📊 Comandos de Monitoreo

### Performance Monitoring
```bash
# Memoria y CPU (Linux/Mac)
top -p $(pgrep -f "python manage.py runserver")

# Conexiones de red
netstat -an | grep :8000

# Espacio en disco
df -h

# Procesos Python
ps aux | grep python
```

### Application Monitoring
```bash
# Logs en tiempo real
tail -f *.log

# Verificar puerto ocupado
lsof -i :8000
lsof -i :5173

# Matar proceso por puerto
kill -9 $(lsof -ti:8000)
```

## 🚨 Comandos de Emergencia

### Recuperación de Datos
```bash
# Backup rápido
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)

# Restaurar backup
cp db.sqlite3.backup.YYYYMMDD_HHMMSS db.sqlite3

# Reset completo (DESTRUCTIVO)
rm db.sqlite3
python manage.py migrate
python manage.py loaddata initial_data.json
```

### Limpieza de Caché
```bash
# Backend - limpiar cache Python
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Frontend - limpiar cache npm
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Git - limpiar archivos no tracked
git clean -fd
```

## 💡 Shortcuts Útiles

### Aliases Recomendados (Bash/Zsh)
```bash
# Agregar a ~/.bashrc o ~/.zshrc
alias dj="python manage.py"
alias djrun="python manage.py runserver"
alias djtest="python manage.py test"
alias djmigrate="python manage.py makemigrations && python manage.py migrate"
alias npmdev="npm run dev"
alias npmbuild="npm run build"

# Recargar configuración
source ~/.bashrc  # o ~/.zshrc
```

### VS Code Tasks (tasks.json)
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Django: Run Server",
      "type": "shell",
      "command": "python",
      "args": ["manage.py", "runserver"],
      "options": { "cwd": "${workspaceFolder}/BackEnd" }
    },
    {
      "label": "React: Dev Server",
      "type": "shell",
      "command": "npm",
      "args": ["run", "dev"],
      "options": { "cwd": "${workspaceFolder}/FrontEnd/SuperVisorioApp" }
    }
  ]
}
```

## 📚 Referencias Rápidas

### Puertos por Defecto
- Django Backend: http://localhost:8000
- React Frontend: http://localhost:5173  
- Django Admin: http://localhost:8000/admin

### Credenciales por Defecto
- Admin User: admin / (contraseña que configuraste)
- Database: SQLite3 (db.sqlite3)

### Archivos Importantes
- Backend Config: `BackEnd/opcpr_project/settings.py`
- Frontend Config: `FrontEnd/SuperVisorioApp/vite.config.ts`
- API Routes: `BackEnd/main_app/urls.py`
- React Routes: `FrontEnd/SuperVisorioApp/app/routes.ts`
