from django import template
from roles.models import RolEnCategoria, Permiso

register = template.Library()

@register.filter(name="tiene_permiso")
def tiene_permiso(usuario, permiso_nombre):
    categorias = RolEnCategoria.objects.filter(usuario=usuario)
    permisos = Permiso.objects.none()
    for rol_categoria in categorias:
        permisos = permisos | rol_categoria.rol.permisos.all()
    return permisos.filter(nombre=permiso_nombre).exists()
