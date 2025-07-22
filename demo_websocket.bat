@echo off
echo ==========================================
echo  DEMO: Sistema Multi-Protocolo
echo ==========================================
echo.

cd /d "%~dp0BackEnd"

echo 🌐 Iniciando servidor WebSocket de ejemplo...
echo   Puerto: 8765
echo   Variables simuladas: temperature_1, pressure_1, motor_1_status
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python opcpr_project\websocket_server_example.py
