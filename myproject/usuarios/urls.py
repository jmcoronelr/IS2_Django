from django.urls import include, path
from . import views
from .views import CustomLoginView, CustomLogoutView
app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registrar_usuario, name="registro"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password_reset/', views.registrar_usuario, name='password_reset') #Aun falta
]