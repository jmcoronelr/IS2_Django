from django.urls import path
from . import views

urlpatterns = [
    path('', views.flujos_home, name='flujos_home'),  # Ruta para el tablero Kanban
    path('update-content-status/', views.update_content_status, name='update_content_status'),  # Actualización de estado
]