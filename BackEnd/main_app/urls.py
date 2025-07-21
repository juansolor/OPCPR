from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views



# Router para API REST
router = DefaultRouter()

urlpatterns = [
    # URLs de la aplicación
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # API URLs
    path('api/', include(router.urls)),
    path('api/health/', views.health_check, name='health_check'),
    path('api/supervisorio/', views.supervisorio_opcua, name='supervisorio_opcua'),
    
    # URLs de autenticación
    path('api/auth/register/', views.register_user, name='register_user'),
    path('api/auth/login/', views.login_user, name='login_user'),
    path('api/auth/logout/', views.logout_user, name='logout_user'),
]
