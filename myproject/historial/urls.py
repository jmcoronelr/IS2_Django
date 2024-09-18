from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/historial/', views.historial_content, name='historial_content'),
]