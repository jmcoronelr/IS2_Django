from django.urls import path
from . import views

urlpatterns = [
    path('', views.reportes_home, name='reportes_home'),  # Ruta para la página principal de reportes
    path('reportes/likes-json/', views.reporte_likes_json, name='reporte_likes_json'),
    path('revision-json/', views.reporte_revision_json, name='reporte_revision_json'),  # Nueva ruta para el reporte de revisión
]
