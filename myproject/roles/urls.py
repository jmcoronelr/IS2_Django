from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuario/<int:usuario_id>/', views.ver_usuario, name='ver_usuario'),
    path('usuario/<int:usuario_id>/asignar-rol/', views.asignar_rol, name='asignar_rol'),
    path('crear_rol/', views.crear_rol, name='crear_rol'),
    path('<int:rol_id>/asignar_permisos/', views.asignar_permisos, name='asignar_permisos'),
    path('<int:rol_id>/', views.ver_rol, name='ver_rol'),  # Ver un rol
    path('eliminar/<int:rol_id>/', views.eliminar_rol, name='eliminar_rol'),  # Eliminar un rol
    path('roles/eliminar_asignacion/<int:rol_en_categoria_id>/', views.eliminar_rol_en_categoria, name='eliminar_rol_en_categoria'),
    path('', views.lista_roles, name='lista_roles'),  # Listar todos los roles
]

