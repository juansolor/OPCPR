@echo off
echo ==========================================
echo  SuperVisorioApp - Sistema Multi-Protocolo
echo ==========================================
echo.

echo 📦 Instalando dependencias adicionales...
echo.

cd /d "%~dp0BackEnd"

echo Activando entorno virtual...
call ..\..\.venv\Scripts\activate.bat

echo.
echo Instalando librerías de protocolos...
pip install websockets==14.1
pip install channels==4.1.0
pip install pymodbus==3.7.4
pip install paho-mqtt==2.1.0
pip install aiofiles==24.1.0

echo.
echo 🔄 Ejecutando migraciones...
python manage.py makemigrations
python manage.py migrate

echo.
echo ✅ Sistema multi-protocolo configurado!
echo.
echo 🚀 Para probar el sistema:
echo.
echo 1. Ejecutar servidor WebSocket de ejemplo:
echo    python opcpr_project\websocket_server_example.py
echo.
echo 2. En otra terminal, ejecutar pruebas:
echo    python test_multiprotocol.py
echo.
echo 3. O iniciar el servidor Django:
echo    python manage.py runserver
echo.
echo 📊 Panel de administración: http://localhost:8000/admin/
echo 🌐 API: http://localhost:8000/api/
echo.
pause
