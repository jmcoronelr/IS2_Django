# content/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.content_list, name='content_list'),
    path('create/', views.content_create, name='content_create'),
    path('delete/<int:pk>/', views.content_delete, name='content_delete'),
    path('edit/<int:pk>/', views.content_edit, name='content_edit'),
    path('detail/<int:pk>/', views.content_detail, name='content_detail'),
]
