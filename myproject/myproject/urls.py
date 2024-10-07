"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('content/', include('content.urls')),
    path('plantillas/', include('Plantillas.urls')),
    path('roles/', include('roles.urls')),
    path('', views.home, name='home'),
    path('usuarios/', include('usuarios.urls')),
    path('sistema/', views.sistema, name="sistema"),
    path('accounts/', include('allauth.urls')),
    path('categorias/', include('Categorias.urls')),
    path('flujos/', include('flujos.urls')),
    path('reportes/', include('reportes.urls')), 
    path('historial/', include('historial.urls')), 
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)