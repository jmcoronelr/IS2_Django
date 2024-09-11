from django.urls import path
from . import views

urlpatterns = [
    path('', views.role_list, name='role_list'),
    path('create/', views.role_create, name='role_create'),
    path('<int:pk>/edit/', views.role_update, name='role_update'),
    path('<int:pk>/delete/', views.role_delete, name='role_delete'),
]

