from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    OpcUaServer, VariableType, OpcUaVariable, VariableReading,
    ConnectionLog, Alarm, UserProfile, SystemConfiguration, AuditLog
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class UserProfileSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_info', 'department', 'phone', 'position',
            'access_level', 'email_notifications', 'last_activity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_info', 'last_activity', 'created_at', 'updated_at']

class OpcUaServerSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = OpcUaServer
        fields = [
            'id', 'name', 'endpoint_url', 'description', 'is_active',
            'username', 'password', 'security_mode', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by_name', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class VariableTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariableType
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

class OpcUaVariableSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    variable_type_name = serializers.CharField(source='variable_type.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    current_value = serializers.SerializerMethodField()
    
    class Meta:
        model = OpcUaVariable
        fields = [
            'id', 'server', 'server_name', 'node_id', 'name', 'description',
            'variable_type', 'variable_type_name', 'data_type', 'unit',
            'min_value', 'max_value', 'is_writable', 'is_monitored',
            'sampling_interval', 'alarm_enabled', 'alarm_high_limit',
            'alarm_low_limit', 'created_by', 'created_by_name',
            'created_at', 'updated_at', 'current_value'
        ]
        read_only_fields = [
            'id', 'server_name', 'variable_type_name', 'created_by_name',
            'created_at', 'updated_at', 'current_value'
        ]
    
    def get_current_value(self, obj):
        """Obtiene el último valor leído de la variable"""
        last_reading = obj.readings.first()
        if last_reading:
            return {
                'value': last_reading.get_value(),
                'timestamp': last_reading.timestamp,
                'quality': last_reading.quality
            }
        return None

class VariableReadingSerializer(serializers.ModelSerializer):
    variable_name = serializers.CharField(source='variable.name', read_only=True)
    server_name = serializers.CharField(source='variable.server.name', read_only=True)
    display_value = serializers.SerializerMethodField()
    
    class Meta:
        model = VariableReading
        fields = [
            'id', 'variable', 'variable_name', 'server_name', 'timestamp',
            'value_boolean', 'value_integer', 'value_float', 'value_string',
            'value_datetime', 'quality', 'status_code', 'display_value'
        ]
        read_only_fields = ['id', 'variable_name', 'server_name', 'display_value']
    
    def get_display_value(self, obj):
        return obj.get_value()

class ConnectionLogSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ConnectionLog
        fields = [
            'id', 'server', 'server_name', 'timestamp', 'event_type',
            'message', 'error_code', 'response_time', 'user', 'user_name'
        ]
        read_only_fields = ['id', 'server_name', 'user_name', 'timestamp']

class AlarmSerializer(serializers.ModelSerializer):
    variable_name = serializers.CharField(source='variable.name', read_only=True)
    server_name = serializers.CharField(source='variable.server.name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.username', read_only=True)
    
    class Meta:
        model = Alarm
        fields = [
            'id', 'variable', 'variable_name', 'server_name', 'timestamp',
            'alarm_type', 'severity', 'message', 'value', 'is_active',
            'acknowledged', 'acknowledged_by', 'acknowledged_by_name',
            'acknowledged_at', 'cleared_at'
        ]
        read_only_fields = [
            'id', 'variable_name', 'server_name', 'acknowledged_by_name',
            'timestamp', 'acknowledged_at', 'cleared_at'
        ]

class SystemConfigurationSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.username', read_only=True)
    parsed_value = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemConfiguration
        fields = [
            'id', 'key', 'value', 'description', 'value_type',
            'created_at', 'updated_at', 'updated_by', 'updated_by_name',
            'parsed_value'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'updated_by_name', 'parsed_value'
        ]
    
    def get_parsed_value(self, obj):
        return obj.get_value()

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'timestamp', 'action', 'model',
            'object_id', 'object_repr', 'changes', 'ip_address', 'user_agent'
        ]
        read_only_fields = [
            'id', 'user_name', 'timestamp', 'action', 'model', 'object_id',
            'object_repr', 'changes', 'ip_address', 'user_agent'
        ]

# Serializers simplificados para las vistas del dashboard
class DashboardVariableSerializer(serializers.ModelSerializer):
    """Serializer ligero para el dashboard"""
    current_value = serializers.SerializerMethodField()
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = OpcUaVariable
        fields = ['id', 'name', 'data_type', 'unit', 'server_name', 'current_value', 'is_monitored']
    
    def get_current_value(self, obj):
        last_reading = obj.readings.first()
        if last_reading:
            return {
                'value': last_reading.get_value(),
                'timestamp': last_reading.timestamp,
                'quality': last_reading.quality
            }
        return None

class DashboardAlarmSerializer(serializers.ModelSerializer):
    """Serializer ligero para alarmas en el dashboard"""
    variable_name = serializers.CharField(source='variable.name', read_only=True)
    server_name = serializers.CharField(source='variable.server.name', read_only=True)
    
    class Meta:
        model = Alarm
        fields = [
            'id', 'variable_name', 'server_name', 'alarm_type',
            'severity', 'message', 'timestamp', 'is_active', 'acknowledged'
        ]

class ConnectionStatusSerializer(serializers.Serializer):
    """Serializer para el estado de conexiones"""
    server_id = serializers.IntegerField()
    server_name = serializers.CharField()
    is_connected = serializers.BooleanField()
    last_connection = serializers.DateTimeField()
    response_time = serializers.FloatField()
    error_count = serializers.IntegerField()
    variables_count = serializers.IntegerField()
    active_alarms_count = serializers.IntegerField()
