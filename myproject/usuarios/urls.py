from django.urls import include, path
from . import views
from .views import CustomLoginView, CustomLogoutView,google_login_redirect
app_name = 'usuarios'

urlpatterns = [
    path('login/google/', google_login_redirect, name='google_login_redirect'),
    path('registro/', views.registrar_usuario, name="registro"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password_reset/', views.registrar_usuario, name='password_reset'), #Aun falta
    path('accounts/', include('allauth.urls')),
    
]