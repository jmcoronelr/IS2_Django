from django import template
from roles.models import RolEnCategoria, Permiso
from django.contrib.auth.models import AnonymousUser

register = template.Library()


@register.filter(name="tiene_permiso")
def tiene_permiso(usuario, permiso_nombre):
    """
    Verifica si el usuario tiene el permiso especificado en alguna de las categorías donde tiene roles.
    Args:
        usuario: El usuario a verificar.
        permiso_nombre: El nombre del permiso a verificar.
    """
    # Verifica si el usuario es anónimo
    if isinstance(usuario, AnonymousUser):
        return False

    # Verifica si el usuario es superuser
    if usuario.is_superuser:
        return True

    # Obtener todos los roles en categorías asignados al usuario
    rol_categorias = RolEnCategoria.objects.filter(usuario=usuario)

    # Verificar si alguno de los roles tiene el permiso requerido en su categoría
    for rol_categoria in rol_categorias:
        if rol_categoria.rol.permisos.filter(nombre=permiso_nombre).exists():
            return True

    # Si no se encontró el permiso en ninguno de los roles, retornar False
    return False


