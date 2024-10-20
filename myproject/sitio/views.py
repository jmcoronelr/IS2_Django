from django.shortcuts import redirect, render
from .models import SiteSettings
from django.contrib.auth.decorators import login_required

@login_required  # Asegurarse de que solo usuarios autenticados puedan acceder
def toggle_maintenance(request):
    # Obtener la configuración de mantenimiento desde la base de datos
    site_settings = SiteSettings.objects.first()

    if request.method == "POST":
        if site_settings:
            # Alternar el estado del modo de mantenimiento solo si es POST
            site_settings.maintenance_mode = not site_settings.maintenance_mode
            site_settings.save()
        return redirect('toggle_maintenance')  # Redirige para evitar reenviar el formulario en una actualización

    # Si es una solicitud GET, solo muestra el estado actual sin cambiar nada
    return render(request, 'toggle_maintenance.html', {'maintenance_mode': site_settings.maintenance_mode})

from django.http import HttpResponse

def maintenance_view(request):
    return HttpResponse("El sitio está en modo de mantenimiento. Por favor, vuelve más tarde.")

