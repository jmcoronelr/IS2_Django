from django.urls import path
from .views import categoria_create, categoria_list, categoria_edit, categoria_delete

urlpatterns = [
    path('create/', categoria_create, name='categoria_create'),
    path('list/', categoria_list, name='categoria_list'),
    path('<int:pk>/edit/', categoria_edit, name='categoria_edit'),
    path('<int:pk>/delete/', categoria_delete, name='categoria_delete'),
]
