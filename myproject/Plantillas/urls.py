from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.plantilla_list, name='plantilla_list'),
    path('create/', views.plantilla_create, name='plantilla_create'),
    path('edit/<int:pk>/', views.plantilla_edit, name='plantilla_edit'),
    path('delete/<int:pk>/', views.plantilla_delete, name='plantilla_delete'),
]
