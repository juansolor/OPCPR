from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import data_views

# Router para API REST
router = DefaultRouter()

# Registrar ViewSets para sistema multi-protocolo
router.register(r'data-servers', data_views.DataServerViewSet, basename='dataserver')
router.register(r'data-variables', data_views.DataVariableViewSet, basename='datavariable')
router.register(r'data-readings', data_views.DataReadingViewSet, basename='datareading')

urlpatterns = [
    # URLs de la aplicación
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # API URLs principales
    path('api/', include(router.urls)),
    path('api/health/', views.health_check, name='health_check'),
    path('api/supervisorio/', views.supervisorio_opcua, name='supervisorio_opcua'),
    
    # URLs del sistema multi-protocolo
    path('api/protocols/supported/', data_views.supported_protocols, name='supported_protocols'),
    path('api/protocols/test-connection/', data_views.test_connection, name='test_connection'),
    path('api/dashboard/summary/', data_views.dashboard_summary, name='dashboard_summary'),
    
    # URLs de autenticación
    path('api/auth/register/', views.register_user, name='register_user'),
    path('api/auth/login/', views.login_user, name='login_user'),
    path('api/auth/logout/', views.logout_user, name='logout_user'),
]
