from django import template
from roles.models import RolEnCategoria, Permiso
from django.contrib.auth.models import AnonymousUser

register = template.Library()

@register.filter(name="tiene_permiso")
def tiene_permiso(usuario, permiso_nombre):
    # Verifica si el usuario es anónimo
    if isinstance(usuario, AnonymousUser):
        return False
    # Verifica si el usuario es superuser
    if usuario.is_superuser:
        return True
    categorias = RolEnCategoria.objects.filter(usuario=usuario)
    permisos = Permiso.objects.none()
    for rol_categoria in categorias:
        permisos = permisos | rol_categoria.rol.permisos.all()
    return permisos.filter(nombre=permiso_nombre).exists()
