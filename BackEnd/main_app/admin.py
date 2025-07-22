from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    OpcUaServer, VariableType, OpcUaVariable, VariableReading,
    ConnectionLog, Alarm, UserProfile, SystemConfiguration, AuditLog,
    DataServer, DataVariable, DataReading
)

# Inline para UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'

# Extender UserAdmin para incluir el perfil
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

# Re-registrar User con el admin personalizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Admin para OpcUaServer
@admin.register(OpcUaServer)
class OpcUaServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'endpoint_url', 'is_active', 'security_mode', 'created_by', 'created_at']
    list_filter = ['is_active', 'security_mode', 'created_at']
    search_fields = ['name', 'endpoint_url', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'endpoint_url', 'description', 'is_active')
        }),
        ('Configuración de seguridad', {
            'fields': ('username', 'password', 'security_mode')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# Admin para VariableType
@admin.register(VariableType)
class VariableTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']

# Admin para OpcUaVariable
@admin.register(OpcUaVariable)
class OpcUaVariableAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'server', 'node_id', 'variable_type', 'data_type', 
        'is_monitored', 'alarm_enabled', 'created_by'
    ]
    list_filter = [
        'server', 'variable_type', 'data_type', 'is_monitored', 
        'is_writable', 'alarm_enabled', 'created_at'
    ]
    search_fields = ['name', 'node_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información básica', {
            'fields': ('server', 'node_id', 'name', 'description', 'variable_type')
        }),
        ('Configuración de datos', {
            'fields': ('data_type', 'unit', 'min_value', 'max_value')
        }),
        ('Configuración de monitoreo', {
            'fields': ('is_writable', 'is_monitored', 'sampling_interval')
        }),
        ('Configuración de alarmas', {
            'fields': ('alarm_enabled', 'alarm_high_limit', 'alarm_low_limit')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

# Admin para VariableReading
@admin.register(VariableReading)
class VariableReadingAdmin(admin.ModelAdmin):
    list_display = ['variable', 'timestamp', 'get_display_value', 'quality', 'status_code']
    list_filter = ['variable__server', 'variable', 'quality', 'timestamp']
    search_fields = ['variable__name', 'variable__node_id']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def get_display_value(self, obj):
        return obj.get_value()
    get_display_value.short_description = 'Valor'
    
    def has_add_permission(self, request):
        return False  # Las lecturas se generan automáticamente

# Admin para ConnectionLog
@admin.register(ConnectionLog)
class ConnectionLogAdmin(admin.ModelAdmin):
    list_display = ['server', 'event_type', 'timestamp', 'response_time', 'user']
    list_filter = ['server', 'event_type', 'timestamp']
    search_fields = ['server__name', 'message']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # Los logs se generan automáticamente

# Admin para Alarm
@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = [
        'variable', 'alarm_type', 'severity', 'is_active', 
        'acknowledged', 'timestamp'
    ]
    list_filter = [
        'variable__server', 'alarm_type', 'severity', 
        'is_active', 'acknowledged', 'timestamp'
    ]
    search_fields = ['variable__name', 'message']
    readonly_fields = ['timestamp', 'acknowledged_at', 'cleared_at']
    date_hierarchy = 'timestamp'
    actions = ['acknowledge_alarms', 'clear_alarms']
    
    def acknowledge_alarms(self, request, queryset):
        queryset.update(
            acknowledged=True, 
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
    acknowledge_alarms.short_description = "Reconocer alarmas seleccionadas"
    
    def clear_alarms(self, request, queryset):
        queryset.update(
            is_active=False,
            cleared_at=timezone.now()
        )
    clear_alarms.short_description = "Aclarar alarmas seleccionadas"

# Admin para UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'department', 'position', 'access_level', 
        'email_notifications', 'last_activity'
    ]
    list_filter = ['department', 'access_level', 'email_notifications']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'department', 'position']
    readonly_fields = ['created_at', 'updated_at', 'last_activity']

# Admin para SystemConfiguration
@admin.register(SystemConfiguration)
class SystemConfigurationAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_type', 'description', 'updated_by', 'updated_at']
    list_filter = ['value_type', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

# Admin para AuditLog
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model', 'object_repr', 'timestamp']
    list_filter = ['action', 'model', 'timestamp']
    search_fields = ['user__username', 'action', 'model', 'object_repr']
    readonly_fields = ['timestamp', 'user', 'action', 'model', 'object_id', 'object_repr', 'changes', 'ip_address', 'user_agent']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # Los logs de auditoría se generan automáticamente
    
    def has_change_permission(self, request, obj=None):
        return False  # Los logs no se pueden modificar
    
    def has_delete_permission(self, request, obj=None):
        return False  # Los logs no se pueden eliminar


# === ADMIN PARA SISTEMA MULTI-PROTOCOLO ===

@admin.register(DataServer)
class DataServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'server_type', 'endpoint_url', 'is_active', 'created_by', 'created_at']
    list_filter = ['server_type', 'is_active', 'created_at']
    search_fields = ['name', 'endpoint_url', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'server_type', 'endpoint_url', 'description', 'is_active')
        }),
        ('Autenticación', {
            'fields': ('username', 'password'),
            'classes': ('collapse',)
        }),
        ('Configuración avanzada', {
            'fields': ('connection_config',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DataVariable)
class DataVariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'server', 'server_type', 'data_type', 'is_monitored', 'is_writable', 'alarm_enabled']
    list_filter = ['server__server_type', 'data_type', 'is_monitored', 'is_writable', 'alarm_enabled', 'created_at']
    search_fields = ['name', 'address', 'description', 'server__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información básica', {
            'fields': ('name', 'server', 'address', 'description', 'variable_type')
        }),
        ('Configuración de datos', {
            'fields': ('data_type', 'unit', 'min_value', 'max_value')
        }),
        ('Monitoreo', {
            'fields': ('is_monitored', 'is_writable', 'sampling_interval')
        }),
        ('Alarmas', {
            'fields': ('alarm_enabled', 'alarm_high_limit', 'alarm_low_limit'),
            'classes': ('collapse',)
        }),
        ('Configuración del protocolo', {
            'fields': ('protocol_config',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def server_type(self, obj):
        return obj.server.server_type
    server_type.short_description = 'Tipo de Servidor'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(DataReading)
class DataReadingAdmin(admin.ModelAdmin):
    list_display = ['variable', 'server_name', 'server_type', 'timestamp', 'get_value_display', 'quality']
    list_filter = ['quality', 'variable__server__server_type', 'timestamp']
    search_fields = ['variable__name', 'variable__server__name']
    readonly_fields = ['timestamp', 'get_value_display']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Variable', {
            'fields': ('variable',)
        }),
        ('Valor', {
            'fields': ('timestamp', 'get_value_display', 'quality')
        }),
        ('Valores por tipo', {
            'fields': ('value_boolean', 'value_integer', 'value_float', 'value_string', 'value_datetime', 'value_json'),
            'classes': ('collapse',)
        }),
        ('Estado y errores', {
            'fields': ('status_code', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Metadatos del protocolo', {
            'fields': ('protocol_metadata',),
            'classes': ('collapse',)
        })
    )
    
    def server_name(self, obj):
        return obj.variable.server.name
    server_name.short_description = 'Servidor'
    
    def server_type(self, obj):
        return obj.variable.server.server_type
    server_type.short_description = 'Tipo'
    
    def get_value_display(self, obj):
        value = obj.get_value()
        if value is None:
            return '-'
        return str(value)
    get_value_display.short_description = 'Valor'
    
    def has_add_permission(self, request):
        return False  # Las lecturas se generan automáticamente
    
    def has_change_permission(self, request, obj=None):
        return False  # Las lecturas no se pueden modificar


# Configuración del sitio de administración
admin.site.site_header = "SuperVisorioApp - Sistema Multi-Protocolo"
admin.site.site_title = "SuperVisorioApp"
admin.site.index_title = "Panel de Administración"
