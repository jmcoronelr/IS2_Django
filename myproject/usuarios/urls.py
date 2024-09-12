from django.urls import include, path
from . import views
from .views import CustomLoginView, CustomLogoutView, google_login_redirect, RecuperarUsuario, profile, ChangePasswordView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

app_name = 'usuarios'

urlpatterns = [
    path('login/google/', google_login_redirect, name='google_login_redirect'),
    path('registro/', views.registrar_usuario, name="registro"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('password_reset/', RecuperarUsuario.as_view(), name='password_reset'), #Aun falta
    path('accounts/', include('allauth.urls')),
    path('profile/', profile, name='users_profile'),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(success_url = reverse_lazy("usuarios:password_reset_complete"), template_name='usuarios/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password_reset_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'),
         name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)