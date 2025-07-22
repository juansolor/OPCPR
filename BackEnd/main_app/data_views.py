# data_views.py
"""
Vistas para el sistema de datos multi-protocolo
Soporta: OPC-UA, OPC Classic, WebSockets, Modbus, MQTT
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from .models import DataServer, DataVariable, DataReading, VariableType
from .serializers import (
    DataServerSerializer, DataVariableSerializer, DataReadingSerializer,
    DataReadingCreateSerializer, DashboardDataVariableSerializer,
    ServerConnectionStatusSerializer
)
from .data_clients import data_manager

logger = logging.getLogger(__name__)


class DataServerViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar servidores de datos multi-protocolo"""
    queryset = DataServer.objects.all()
    serializer_class = DataServerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Asignar usuario creador al crear servidor"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def connect(self, request, pk=None):
        """Conectar a un servidor específico"""
        try:
            server = self.get_object()
            
            # Preparar configuración del servidor
            server_config = {
                'endpoint_url': server.endpoint_url,
                'username': server.username,
                'password': server.password,
                'connection_config': server.get_connection_config()
            }
            
            # Usar asyncio para conectar
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                data_manager.add_server(str(server.id), server.server_type, server_config)
            )
            
            loop.close()
            
            if success:
                return Response({
                    'status': 'connected',
                    'message': f'Conectado exitosamente a {server.name}'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': f'Error conectando a {server.name}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error conectando servidor {pk}: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """Desconectar de un servidor específico"""
        try:
            server = self.get_object()
            
            # Usar asyncio para desconectar
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            loop.run_until_complete(data_manager.remove_server(str(server.id)))
            loop.close()
            
            return Response({
                'status': 'disconnected',
                'message': f'Desconectado de {server.name}'
            })
            
        except Exception as e:
            logger.error(f"Error desconectando servidor {pk}: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Obtener estado de conexión de un servidor"""
        try:
            server = self.get_object()
            status_info = data_manager.get_server_status(str(server.id))
            
            # Enriquecer con información del modelo
            status_info.update({
                'server_name': server.name,
                'server_type': server.server_type,
                'endpoint_url': server.endpoint_url,
                'variables_count': server.datavariable_set.count()
            })
            
            serializer = ServerConnectionStatusSerializer(status_info)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del servidor {pk}: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def all_status(self, request):
        """Obtener estado de todos los servidores"""
        try:
            servers = self.get_queryset()
            status_list = []
            
            for server in servers:
                status_info = data_manager.get_server_status(str(server.id))
                status_info.update({
                    'server_name': server.name,
                    'server_type': server.server_type,
                    'endpoint_url': server.endpoint_url,
                    'variables_count': server.datavariable_set.count()
                })
                status_list.append(status_info)
            
            serializer = ServerConnectionStatusSerializer(status_list, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de servidores: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataVariableViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar variables de datos multi-protocolo"""
    queryset = DataVariable.objects.all()
    serializer_class = DataVariableSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar variables por servidor si se especifica"""
        queryset = DataVariable.objects.all().select_related('server', 'variable_type', 'created_by')
        
        server_id = self.request.query_params.get('server', None)
        if server_id:
            queryset = queryset.filter(server_id=server_id)
        
        server_type = self.request.query_params.get('server_type', None)
        if server_type:
            queryset = queryset.filter(server__server_type=server_type)
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar usuario creador al crear variable"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def read_value(self, request, pk=None):
        """Leer el valor actual de una variable"""
        try:
            variable = self.get_object()
            
            # Usar asyncio para leer
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            value = loop.run_until_complete(
                data_manager.read_variable(
                    str(variable.server.id),
                    variable.address,
                    variable.get_protocol_config()
                )
            )
            
            loop.close()
            
            if value is not None:
                # Crear lectura en la base de datos
                reading = DataReading(
                    variable=variable,
                    timestamp=timezone.now(),
                    quality='GOOD'
                )
                reading.set_value(value)
                reading.save()
                
                return Response({
                    'variable': variable.name,
                    'value': value,
                    'timestamp': reading.timestamp,
                    'quality': reading.quality
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'No se pudo leer la variable'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error leyendo variable {pk}: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def write_value(self, request, pk=None):
        """Escribir un valor a una variable"""
        try:
            variable = self.get_object()
            value = request.data.get('value')
            
            if value is None:
                return Response({
                    'status': 'error',
                    'message': 'Valor requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not variable.is_writable:
                return Response({
                    'status': 'error',
                    'message': 'Variable no es escribible'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Usar asyncio para escribir
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                data_manager.write_variable(
                    str(variable.server.id),
                    variable.address,
                    value,
                    variable.get_protocol_config()
                )
            )
            
            loop.close()
            
            if success:
                # Crear lectura de confirmación
                reading = DataReading(
                    variable=variable,
                    timestamp=timezone.now(),
                    quality='GOOD'
                )
                reading.set_value(value)
                reading.save()
                
                return Response({
                    'variable': variable.name,
                    'value': value,
                    'timestamp': reading.timestamp,
                    'status': 'written'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'No se pudo escribir la variable'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error escribiendo variable {pk}: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """Suscribirse a una variable para recibir actualizaciones"""
        try:
            variable = self.get_object()
            
            # Definir callback para manejar actualizaciones
            def data_callback(address, value, timestamp):
                try:
                    # Crear lectura en la base de datos
                    reading = DataReading(
                        variable=variable,
                        timestamp=datetime.fromisoformat(timestamp.replace('Z', '+00:00')) if isinstance(timestamp, str) else timezone.now(),
                        quality='GOOD'
                    )
                    reading.set_value(value)
                    reading.save()
                    
                    logger.info(f"Nueva lectura para {variable.name}: {value}")
                except Exception as e:
                    logger.error(f"Error guardando lectura: {e}")
            
            # Usar asyncio para suscribirse
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            loop.run_until_complete(
                data_manager.subscribe_variable(
                    str(variable.server.id),
                    variable.address,
                    data_callback,
                    variable.get_protocol_config()
                )
            )
            
            loop.close()
            
            return Response({
                'variable': variable.name,
                'status': 'subscribed',
                'message': f'Suscrito a {variable.name}'
            })
            
        except Exception as e:
            logger.error(f"Error suscribiéndose a variable {pk}: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Obtener variables para el dashboard"""
        try:
            # Obtener solo variables monitoreadas
            variables = self.get_queryset().filter(is_monitored=True)
            
            # Usar serializer ligero
            serializer = DashboardDataVariableSerializer(variables, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error obteniendo variables para dashboard: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consultar lecturas de datos (solo lectura)"""
    queryset = DataReading.objects.all()
    serializer_class = DataReadingSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar lecturas por variable, servidor o fechas"""
        queryset = DataReading.objects.all().select_related(
            'variable', 'variable__server'
        ).order_by('-timestamp')
        
        # Filtros
        variable_id = self.request.query_params.get('variable', None)
        if variable_id:
            queryset = queryset.filter(variable_id=variable_id)
        
        server_id = self.request.query_params.get('server', None)
        if server_id:
            queryset = queryset.filter(variable__server_id=server_id)
        
        # Filtros de fecha
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__gte=start_dt)
            except ValueError:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__lte=end_dt)
            except ValueError:
                pass
        
        # Limitar resultados por defecto
        limit = self.request.query_params.get('limit', 1000)
        try:
            limit = int(limit)
            queryset = queryset[:limit]
        except ValueError:
            queryset = queryset[:1000]
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Obtener las últimas lecturas de todas las variables"""
        try:
            # Obtener la última lectura por variable
            latest_readings = []
            
            for variable in DataVariable.objects.filter(is_monitored=True):
                last_reading = variable.readings.first()
                if last_reading:
                    latest_readings.append(last_reading)
            
            serializer = DataReadingSerializer(latest_readings, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error obteniendo últimas lecturas: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# API Views adicionales
@api_view(['GET'])
def supported_protocols(request):
    """Obtener lista de protocolos soportados"""
    try:
        from .data_clients import DataClientFactory
        
        protocols = []
        for protocol_type in DataClientFactory.get_supported_types():
            protocols.append({
                'type': protocol_type,
                'name': protocol_type.replace('_', ' ').title(),
                'description': f'Protocolo {protocol_type.replace("_", " ")}'
            })
        
        return Response({
            'protocols': protocols,
            'count': len(protocols)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo protocolos soportados: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def test_connection(request):
    """Probar conexión a un servidor sin guardarlo"""
    try:
        data = request.data
        
        server_config = {
            'endpoint_url': data.get('endpoint_url'),
            'username': data.get('username'),
            'password': data.get('password'),
            'connection_config': data.get('connection_config', {})
        }
        
        server_type = data.get('server_type')
        
        # Usar asyncio para probar conexión
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from .data_clients import DataClientFactory
        client = DataClientFactory.create_client(server_type, server_config)
        
        if client:
            success = loop.run_until_complete(client.connect())
            if success:
                loop.run_until_complete(client.disconnect())
                loop.close()
                
                return Response({
                    'status': 'success',
                    'message': 'Conexión exitosa'
                })
            else:
                loop.close()
                return Response({
                    'status': 'error',
                    'message': 'No se pudo conectar al servidor'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            loop.close()
            return Response({
                'status': 'error',
                'message': 'Tipo de servidor no soportado'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error probando conexión: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def dashboard_summary(request):
    """Obtener resumen del dashboard multi-protocolo"""
    try:
        # Estadísticas de servidores
        total_servers = DataServer.objects.count()
        active_servers = DataServer.objects.filter(is_active=True).count()
        
        # Estadísticas de variables
        total_variables = DataVariable.objects.count()
        monitored_variables = DataVariable.objects.filter(is_monitored=True).count()
        
        # Estadísticas de lecturas (últimas 24 horas)
        last_24h = timezone.now() - timedelta(hours=24)
        recent_readings = DataReading.objects.filter(timestamp__gte=last_24h).count()
        
        # Estado de conexiones
        connected_servers = 0
        for server in DataServer.objects.filter(is_active=True):
            status = data_manager.get_server_status(str(server.id))
            if status.get('connected', False):
                connected_servers += 1
        
        # Protocolos en uso
        protocols_in_use = DataServer.objects.values_list('server_type', flat=True).distinct()
        
        return Response({
            'servers': {
                'total': total_servers,
                'active': active_servers,
                'connected': connected_servers
            },
            'variables': {
                'total': total_variables,
                'monitored': monitored_variables
            },
            'readings': {
                'last_24h': recent_readings
            },
            'protocols': list(protocols_in_use),
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen del dashboard: {e}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
