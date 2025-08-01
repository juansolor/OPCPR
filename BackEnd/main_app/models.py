from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

# === MODELOS PARA SISTEMA DE SUPERVISIÓN OPC-UA ===

# === MODELO BASE PARA SERVIDORES DE DATOS ===

class DataServer(models.Model):
    """Modelo base para almacenar información de servidores de datos"""
    SERVER_TYPES = [
        ('OPC_UA', 'OPC-UA'),
        ('OPC_CLASSIC', 'OPC Classic'),
        ('WEBSOCKET', 'WebSocket'),
        ('MODBUS', 'Modbus TCP'),
        ('MQTT', 'MQTT'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre del servidor")
    server_type = models.CharField(max_length=20, choices=SERVER_TYPES, verbose_name="Tipo de servidor")
    endpoint_url = models.CharField(max_length=500, verbose_name="URL/Endpoint del servidor")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    # Autenticación
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Usuario")
    password = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contraseña")
    
    # Configuraciones específicas por tipo (JSON)
    connection_config = models.JSONField(default=dict, blank=True, verbose_name="Configuración de conexión")
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    
    class Meta:
        verbose_name = "Servidor de Datos"
        verbose_name_plural = "Servidores de Datos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.server_type})"
    
    def get_connection_config(self):
        """Obtiene la configuración específica del servidor"""
        default_configs = {
            'OPC_UA': {
                'security_mode': 'NONE',
                'certificate_path': '',
                'private_key_path': ''
            },
            'OPC_CLASSIC': {
                'clsid': '',
                'prog_id': '',
                'update_rate': 1000
            },
            'WEBSOCKET': {
                'protocol': 'ws',
                'heartbeat_interval': 30,
                'reconnect_attempts': 5
            },
            'MODBUS': {
                'port': 502,
                'unit_id': 1,
                'timeout': 3
            },
            'MQTT': {
                'port': 1883,
                'keep_alive': 60,
                'qos': 1
            }
        }
        
        config = default_configs.get(self.server_type, {})
        config.update(self.connection_config)
        return config


class OpcUaServer(models.Model):
    """Modelo para almacenar información de servidores OPC-UA (Compatibilidad)"""
    name = models.CharField(max_length=100, verbose_name="Nombre del servidor")
    endpoint_url = models.URLField(verbose_name="URL del endpoint")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Usuario")
    password = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contraseña")
    security_mode = models.CharField(
        max_length=20,
        choices=[
            ('NONE', 'Sin seguridad'),
            ('SIGN', 'Solo firma'),
            ('SIGN_ENCRYPT', 'Firma y encriptación')
        ],
        default='NONE',
        verbose_name="Modo de seguridad"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    
    class Meta:
        verbose_name = "Servidor OPC-UA"
        verbose_name_plural = "Servidores OPC-UA"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.endpoint_url})"


class VariableType(models.Model):
    """Tipos de variables OPC-UA"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nombre del tipo")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Tipo de Variable"
        verbose_name_plural = "Tipos de Variables"
    
    def __str__(self):
        return self.name


class DataVariable(models.Model):
    """Modelo para variables monitoreadas desde cualquier tipo de servidor"""
    server = models.ForeignKey(DataServer, on_delete=models.CASCADE, verbose_name="Servidor")
    address = models.CharField(max_length=500, verbose_name="Dirección/NodeID/Tag")
    name = models.CharField(max_length=100, verbose_name="Nombre de la variable")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    variable_type = models.ForeignKey(VariableType, on_delete=models.CASCADE, verbose_name="Tipo de variable")
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('BOOLEAN', 'Boolean'),
            ('INTEGER', 'Entero'),
            ('FLOAT', 'Decimal'),
            ('STRING', 'Texto'),
            ('DATETIME', 'Fecha y hora'),
            ('ARRAY', 'Array'),
            ('JSON', 'JSON Object')
        ],
        verbose_name="Tipo de dato"
    )
    unit = models.CharField(max_length=20, blank=True, null=True, verbose_name="Unidad")
    min_value = models.FloatField(blank=True, null=True, verbose_name="Valor mínimo")
    max_value = models.FloatField(blank=True, null=True, verbose_name="Valor máximo")
    is_writable = models.BooleanField(default=False, verbose_name="Es escribible")
    is_monitored = models.BooleanField(default=True, verbose_name="Es monitorizada")
    sampling_interval = models.IntegerField(default=1000, verbose_name="Intervalo de muestreo (ms)")
    
    # Configuración específica por protocolo
    protocol_config = models.JSONField(default=dict, blank=True, verbose_name="Configuración del protocolo")
    
    # Sistema de alarmas
    alarm_enabled = models.BooleanField(default=False, verbose_name="Alarmas habilitadas")
    alarm_high_limit = models.FloatField(blank=True, null=True, verbose_name="Límite alto de alarma")
    alarm_low_limit = models.FloatField(blank=True, null=True, verbose_name="Límite bajo de alarma")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    
    class Meta:
        verbose_name = "Variable de Datos"
        verbose_name_plural = "Variables de Datos"
        unique_together = ['server', 'address']
        ordering = ['server', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.server.name})"
    
    def get_protocol_config(self):
        """Obtiene la configuración específica del protocolo"""
        default_configs = {
            'OPC_UA': {
                'namespace_index': 2,
                'identifier_type': 'numeric'
            },
            'OPC_CLASSIC': {
                'group_name': 'Group1',
                'item_name': self.address
            },
            'WEBSOCKET': {
                'topic': self.address,
                'message_format': 'json'
            },
            'MODBUS': {
                'register_type': 'holding',
                'register_address': int(self.address) if self.address.isdigit() else 0,
                'data_format': 'uint16'
            },
            'MQTT': {
                'topic': self.address,
                'retained': False
            }
        }
        
        config = default_configs.get(self.server.server_type, {})
        config.update(self.protocol_config)
        return config


class OpcUaVariable(models.Model):
    """Modelo para variables OPC-UA monitoreadas (Compatibilidad)"""
    server = models.ForeignKey(OpcUaServer, on_delete=models.CASCADE, verbose_name="Servidor")
    node_id = models.CharField(max_length=200, verbose_name="Node ID")
    name = models.CharField(max_length=100, verbose_name="Nombre de la variable")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    variable_type = models.ForeignKey(VariableType, on_delete=models.CASCADE, verbose_name="Tipo de variable")
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('BOOLEAN', 'Boolean'),
            ('INTEGER', 'Entero'),
            ('FLOAT', 'Decimal'),
            ('STRING', 'Texto'),
            ('DATETIME', 'Fecha y hora')
        ],
        verbose_name="Tipo de dato"
    )
    unit = models.CharField(max_length=20, blank=True, null=True, verbose_name="Unidad")
    min_value = models.FloatField(blank=True, null=True, verbose_name="Valor mínimo")
    max_value = models.FloatField(blank=True, null=True, verbose_name="Valor máximo")
    is_writable = models.BooleanField(default=False, verbose_name="Es escribible")
    is_monitored = models.BooleanField(default=True, verbose_name="Es monitorizada")
    sampling_interval = models.IntegerField(default=1000, verbose_name="Intervalo de muestreo (ms)")
    alarm_enabled = models.BooleanField(default=False, verbose_name="Alarmas habilitadas")
    alarm_high_limit = models.FloatField(blank=True, null=True, verbose_name="Límite alto de alarma")
    alarm_low_limit = models.FloatField(blank=True, null=True, verbose_name="Límite bajo de alarma")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    
    class Meta:
        verbose_name = "Variable OPC-UA"
        verbose_name_plural = "Variables OPC-UA"
        unique_together = ['server', 'node_id']
        ordering = ['server', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.server.name})"


class DataReading(models.Model):
    """Modelo para almacenar lecturas de variables de cualquier protocolo"""
    variable = models.ForeignKey(DataVariable, on_delete=models.CASCADE, related_name='readings', verbose_name="Variable")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Marca de tiempo")
    
    # Valores por tipo de dato
    value_boolean = models.BooleanField(blank=True, null=True, verbose_name="Valor boolean")
    value_integer = models.BigIntegerField(blank=True, null=True, verbose_name="Valor entero")
    value_float = models.FloatField(blank=True, null=True, verbose_name="Valor decimal")
    value_string = models.TextField(blank=True, null=True, verbose_name="Valor texto")
    value_datetime = models.DateTimeField(blank=True, null=True, verbose_name="Valor fecha")
    value_json = models.JSONField(blank=True, null=True, verbose_name="Valor JSON")
    
    # Calidad y estado
    quality = models.CharField(
        max_length=20,
        choices=[
            ('GOOD', 'Buena'),
            ('BAD', 'Mala'),
            ('UNCERTAIN', 'Incierta'),
            ('TIMEOUT', 'Timeout'),
            ('ERROR', 'Error')
        ],
        default='GOOD',
        verbose_name="Calidad"
    )
    status_code = models.IntegerField(blank=True, null=True, verbose_name="Código de estado")
    error_message = models.TextField(blank=True, null=True, verbose_name="Mensaje de error")
    
    # Metadatos del protocolo
    protocol_metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadatos del protocolo")
    
    class Meta:
        verbose_name = "Lectura de Datos"
        verbose_name_plural = "Lecturas de Datos"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['variable', '-timestamp']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['quality']),
        ]
    
    def get_value(self):
        """Obtiene el valor según el tipo de dato"""
        if self.variable.data_type == 'BOOLEAN':
            return self.value_boolean
        elif self.variable.data_type == 'INTEGER':
            return self.value_integer
        elif self.variable.data_type == 'FLOAT':
            return self.value_float
        elif self.variable.data_type == 'STRING':
            return self.value_string
        elif self.variable.data_type == 'DATETIME':
            return self.value_datetime
        elif self.variable.data_type == 'JSON':
            return self.value_json
        return None
    
    def set_value(self, value):
        """Establece el valor según el tipo de dato"""
        try:
            if self.variable.data_type == 'BOOLEAN':
                self.value_boolean = bool(value)
            elif self.variable.data_type == 'INTEGER':
                self.value_integer = int(value)
            elif self.variable.data_type == 'FLOAT':
                self.value_float = float(value)
            elif self.variable.data_type == 'STRING':
                self.value_string = str(value)
            elif self.variable.data_type == 'DATETIME':
                self.value_datetime = value
            elif self.variable.data_type == 'JSON':
                self.value_json = value if isinstance(value, (dict, list)) else json.loads(str(value))
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            self.quality = 'ERROR'
            self.error_message = f"Error convertir valor: {str(e)}"
    
    def __str__(self):
        return f"{self.variable.name}: {self.get_value()} ({self.timestamp})"


class VariableReading(models.Model):
    """Modelo para almacenar lecturas de variables (Compatibilidad)"""
    variable = models.ForeignKey(OpcUaVariable, on_delete=models.CASCADE, related_name='readings', verbose_name="Variable")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Marca de tiempo")
    value_boolean = models.BooleanField(blank=True, null=True, verbose_name="Valor boolean")
    value_integer = models.BigIntegerField(blank=True, null=True, verbose_name="Valor entero")
    value_float = models.FloatField(blank=True, null=True, verbose_name="Valor decimal")
    value_string = models.TextField(blank=True, null=True, verbose_name="Valor texto")
    value_datetime = models.DateTimeField(blank=True, null=True, verbose_name="Valor fecha")
    quality = models.CharField(
        max_length=20,
        choices=[
            ('GOOD', 'Buena'),
            ('BAD', 'Mala'),
            ('UNCERTAIN', 'Incierta')
        ],
        default='GOOD',
        verbose_name="Calidad"
    )
    status_code = models.IntegerField(blank=True, null=True, verbose_name="Código de estado")
    
    class Meta:
        verbose_name = "Lectura de Variable"
        verbose_name_plural = "Lecturas de Variables"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['variable', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def get_value(self):
        """Obtiene el valor según el tipo de dato"""
        if self.variable.data_type == 'BOOLEAN':
            return self.value_boolean
        elif self.variable.data_type == 'INTEGER':
            return self.value_integer
        elif self.variable.data_type == 'FLOAT':
            return self.value_float
        elif self.variable.data_type == 'STRING':
            return self.value_string
        elif self.variable.data_type == 'DATETIME':
            return self.value_datetime
        return None
    
    def set_value(self, value):
        """Establece el valor según el tipo de dato"""
        if self.variable.data_type == 'BOOLEAN':
            self.value_boolean = bool(value)
        elif self.variable.data_type == 'INTEGER':
            self.value_integer = int(value)
        elif self.variable.data_type == 'FLOAT':
            self.value_float = float(value)
        elif self.variable.data_type == 'STRING':
            self.value_string = str(value)
        elif self.variable.data_type == 'DATETIME':
            self.value_datetime = value
    
    def __str__(self):
        return f"{self.variable.name}: {self.get_value()} @ {self.timestamp}"


class ConnectionLog(models.Model):
    """Modelo para registrar conexiones y desconexiones"""
    server = models.ForeignKey(OpcUaServer, on_delete=models.CASCADE, related_name='connection_logs', verbose_name="Servidor")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Marca de tiempo")
    event_type = models.CharField(
        max_length=20,
        choices=[
            ('CONNECT', 'Conexión'),
            ('DISCONNECT', 'Desconexión'),
            ('ERROR', 'Error'),
            ('RECONNECT', 'Reconexión')
        ],
        verbose_name="Tipo de evento"
    )
    message = models.TextField(blank=True, null=True, verbose_name="Mensaje")
    error_code = models.IntegerField(blank=True, null=True, verbose_name="Código de error")
    response_time = models.FloatField(blank=True, null=True, verbose_name="Tiempo de respuesta (ms)")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Usuario")
    
    class Meta:
        verbose_name = "Log de Conexión"
        verbose_name_plural = "Logs de Conexión"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.server.name} - {self.event_type} @ {self.timestamp}"


class Alarm(models.Model):
    """Modelo para alarmas del sistema"""
    variable = models.ForeignKey(OpcUaVariable, on_delete=models.CASCADE, related_name='alarms', verbose_name="Variable")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Marca de tiempo")
    alarm_type = models.CharField(
        max_length=20,
        choices=[
            ('HIGH', 'Valor alto'),
            ('LOW', 'Valor bajo'),
            ('QUALITY', 'Calidad'),
            ('COMMUNICATION', 'Comunicación'),
            ('SYSTEM', 'Sistema')
        ],
        verbose_name="Tipo de alarma"
    )
    severity = models.CharField(
        max_length=10,
        choices=[
            ('LOW', 'Baja'),
            ('MEDIUM', 'Media'),
            ('HIGH', 'Alta'),
            ('CRITICAL', 'Crítica')
        ],
        default='MEDIUM',
        verbose_name="Severidad"
    )
    message = models.TextField(verbose_name="Mensaje")
    value = models.FloatField(blank=True, null=True, verbose_name="Valor que causó la alarma")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    acknowledged = models.BooleanField(default=False, verbose_name="Reconocida")
    acknowledged_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Reconocida por")
    acknowledged_at = models.DateTimeField(blank=True, null=True, verbose_name="Reconocida en")
    cleared_at = models.DateTimeField(blank=True, null=True, verbose_name="Aclarada en")
    
    class Meta:
        verbose_name = "Alarma"
        verbose_name_plural = "Alarmas"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.variable.name} - {self.alarm_type} - {self.severity}"


class UserProfile(models.Model):
    """Perfil extendido de usuario para el sistema"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cargo")
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('VIEWER', 'Solo lectura'),
            ('OPERATOR', 'Operador'),
            ('SUPERVISOR', 'Supervisor'),
            ('ADMIN', 'Administrador')
        ],
        default='VIEWER',
        verbose_name="Nivel de acceso"
    )
    email_notifications = models.BooleanField(default=True, verbose_name="Notificaciones por email")
    last_activity = models.DateTimeField(blank=True, null=True, verbose_name="Última actividad")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"


class SystemConfiguration(models.Model):
    """Configuraciones del sistema"""
    key = models.CharField(max_length=100, unique=True, verbose_name="Clave")
    value = models.TextField(verbose_name="Valor")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    value_type = models.CharField(
        max_length=20,
        choices=[
            ('STRING', 'Texto'),
            ('INTEGER', 'Entero'),
            ('FLOAT', 'Decimal'),
            ('BOOLEAN', 'Booleano'),
            ('JSON', 'JSON')
        ],
        default='STRING',
        verbose_name="Tipo de valor"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Actualizado por")
    
    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuraciones del Sistema"
        ordering = ['key']
    
    def get_value(self):
        """Obtiene el valor convertido según su tipo"""
        if self.value_type == 'INTEGER':
            return int(self.value)
        elif self.value_type == 'FLOAT':
            return float(self.value)
        elif self.value_type == 'BOOLEAN':
            return self.value.lower() in ['true', '1', 'yes']
        elif self.value_type == 'JSON':
            return json.loads(self.value)
        return self.value
    
    def __str__(self):
        return f"{self.key}: {self.value}"


class AuditLog(models.Model):
    """Log de auditoría para el sistema"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Usuario")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Marca de tiempo")
    action = models.CharField(max_length=100, verbose_name="Acción")
    model = models.CharField(max_length=100, verbose_name="Modelo")
    object_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID del objeto")
    object_repr = models.CharField(max_length=200, blank=True, null=True, verbose_name="Representación del objeto")
    changes = models.JSONField(blank=True, null=True, verbose_name="Cambios")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Log de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model} @ {self.timestamp}"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
