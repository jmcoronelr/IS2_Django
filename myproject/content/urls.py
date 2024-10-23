# content/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.content_list, name='content_list'),  # Listar contenidos
    path('create/', views.content_create_edit, name='content_create'),  # Crear contenido
    path('edit/<int:pk>/', views.content_create_edit, name='content_edit'),  # Editar contenido
    path('delete/<int:pk>/', views.content_delete, name='content_delete'),  # Eliminar contenido
    path('detail/<int:pk>/', views.content_detail, name='content_detail'),  # Detalle de contenido
    path('<int:plantilla_id>/get_blocks/', views.get_plantilla_blocks, name='get_plantilla_blocks'),  # Obtener bloques de plantilla
    path('detail/<int:pk>/comentario/', views.agregar_comentario, name='agregar_comentario'),
    path('review/', views.review_list, name='review_list'),  # Listar contenidos en Revision
    path('review/detail/<int:pk>/', views.review_detail, name='review_detail'),  # Revison del contenido
    path('switch-state/<int:pk>/', views.cambiar_estado_contenido, name='switch_state'),
    path('like/<int:pk>/', views.like_content, name='like_content'),
    path('dislike/<int:pk>/', views.dislike_content, name='dislike_content'),    
]
