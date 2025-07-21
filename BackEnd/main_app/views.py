from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
import json
from .opcua_client import SIGNALS, LeerOpcUa, EscribirOpcUa, OpcUaServer, simular_datos_opcua

# Vista principal
def home(request):
    context = {
        'title': 'OPCPR Project',
        'message': '¡Bienvenido al proyecto OPCPR!'
    }
    return render(request, 'main_app/home.html', context)

# Vista about
def about(request):
    context = {
        'title': 'Acerca de',
        'message': 'Esta es una aplicación Django con REST API'
    }
    return render(request, 'main_app/about.html', context)

# API para verificar el estado del servidor
@api_view(['GET'])
def health_check(request):
    """
    Endpoint para verificar que la API está funcionando
    """
    data = {
        'status': 'ok',
        'message': 'API funcionando correctamente',
        'version': '1.0.0'
    }
    return Response(data, status=status.HTTP_200_OK)

# API para obtener información del servidor
@api_view(['GET'])
def server_info(request):
    """
    Endpoint para obtener información del servidor
    """
    data = {
        'status': 'ok',
        'message': 'Información del servidor',
        'version': '1.0.0'
    }
    return Response(data, status=status.HTTP_200_OK)

# backend/views.py

@csrf_exempt
@api_view(['GET', 'POST'])
def supervisorio_opcua(request):
    url = request.GET.get("url", "opc.tcp://localhost:4840") if request.method == 'GET' else request.data.get("url", "opc.tcp://localhost:4840")
    
    if request.method == 'GET':
        # Leer datos del servidor OPC UA
        inputs = LeerOpcUa(url, SIGNALS)
        
        # Si no se pueden obtener datos reales, usar datos simulados
        if not inputs:
            inputs = simular_datos_opcua()
            return Response({
                "status": "success",
                "method": "GET",
                "url": url,
                "data": inputs,
                "warning": "Servidor OPC UA no disponible - usando datos simulados"
            }, status=status.HTTP_200_OK)
        
        return Response({
            "status": "success",
            "method": "GET",
            "url": url,
            "data": inputs
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Escribir datos al servidor OPC UA
        try:
            # Obtener los datos a escribir desde el request
            write_data = request.data.get("data", {})
            
            if not write_data:
                return Response({"error": "No se proporcionaron datos para escribir"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Escribir datos al servidor OPC UA
            outputs = EscribirOpcUa(url, write_data)
            
            if outputs is None:
                # Simular escritura exitosa si no hay servidor
                return Response({
                    "status": "success",
                    "method": "POST",
                    "url": url,
                    "message": "Datos escritos correctamente (simulado)",
                    "written_data": write_data,
                    "warning": "Servidor OPC UA no disponible - operación simulada",
                    "response": {
                        "success": True,
                        "written_nodes": len(write_data),
                        "simulated": True
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({
                "status": "success",
                "method": "POST",
                "url": url,
                "message": "Datos escritos correctamente",
                "written_data": write_data,
                "response": outputs
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": f"Error en la operación POST: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# === VIEWS DE AUTENTICACIÓN ===

@api_view(['POST'])
@csrf_exempt
def register_user(request):
    """
    Registrar un nuevo usuario
    """
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        
        # Validar datos requeridos
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        errors = {}
        
        for field in required_fields:
            if not data.get(field):
                errors[field] = f'{field.replace("_", " ").title()} es requerido'
        
        # Validaciones específicas
        if data.get('username') and len(data['username']) < 3:
            errors['username'] = 'El usuario debe tener al menos 3 caracteres'
            
        if data.get('password') and len(data['password']) < 6:
            errors['password'] = 'La contraseña debe tener al menos 6 caracteres'
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=data.get('username')).exists():
            errors['username'] = 'Este nombre de usuario ya existe'
            
        if User.objects.filter(email=data.get('email')).exists():
            errors['email'] = 'Este email ya está registrado'
        
        if errors:
            return Response({
                "status": "error",
                "message": "Error de validación",
                "errors": errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear el usuario
        user = User.objects.create(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            password=make_password(data['password'])  # Hasher la contraseña
        )
        
        return Response({
            "status": "success",
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response({
            "status": "error",
            "message": "Datos JSON inválidos"
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Error interno del servidor: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@csrf_exempt
def login_user(request):
    """
    Iniciar sesión de usuario
    """
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return Response({
                "status": "error",
                "message": "Usuario y contraseña son requeridos"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Autenticar usuario
        user = authenticate(username=username, password=password)
        
        if user is not None:
            # Crear o obtener token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "status": "success",
                "message": "Inicio de sesión exitoso",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "Credenciales incorrectas"
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except json.JSONDecodeError:
        return Response({
            "status": "error",
            "message": "Datos JSON inválidos"
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Error interno del servidor: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def logout_user(request):
    """
    Cerrar sesión de usuario (eliminar token)
    """
    try:
        token = request.auth
        if token:
            token.delete()
            return Response({
                "status": "success",
                "message": "Sesión cerrada correctamente"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": "No hay sesión activa"
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Error interno del servidor: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
