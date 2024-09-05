from django.urls import path
from . import views

urlpatterns = [
    path('usuario/<int:usuario_id>/', views.ver_usuario, name='ver_usuario'),
    path('usuario/<int:usuario_id>/asignar-rol/', views.asignar_rol, name='asignar_rol'),
    path('crear_rol/', views.crear_rol, name='crear_rol'),
    path('<int:rol_id>/asignar_permisos/', views.asignar_permisos, name='asignar_permisos'),
    path('<int:rol_id>/', views.ver_rol, name='ver_rol'),  # Ver un rol
    path('', views.lista_roles, name='lista_roles'),  # Listar todos los roles
]

