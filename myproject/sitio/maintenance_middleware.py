from django.shortcuts import redirect
from django.urls import reverse
from .models import SiteSettings

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Obtener la configuración de mantenimiento desde la base de datos
        site_settings, created = SiteSettings.objects.get_or_create(id=1)

        # Asegúrate de que las rutas críticas y la página de mantenimiento están excluidas
        excluded_paths = [
            reverse('admin:index'),  # Página de administración de Django
            reverse('home'),         # Página de inicio
            reverse('maintenance'),  # Página de mantenimiento
        ]

        # Verificar si el modo de mantenimiento está activado
        if site_settings.maintenance_mode:
            # Excluir todas las rutas que empiecen con '/usuario/' o estén en excluded_paths
            if request.path.startswith('/usuarios/') or request.path in excluded_paths:
                print("Ruta excluida del mantenimiento.")
                return self.get_response(request)

            # Permitir acceso a usuarios con permisos de staff (administradores)
            if request.user.is_authenticated and request.user.is_staff:
                print("Acceso permitido a un usuario staff.")
                return self.get_response(request)

            # Si no es administrador y no está en una ruta crítica, redirigir a la página de mantenimiento
            print("Redirigiendo a la página de mantenimiento.")
            return redirect('maintenance')

        # Si el modo de mantenimiento está desactivado, continuar normalmente
        return self.get_response(request)

