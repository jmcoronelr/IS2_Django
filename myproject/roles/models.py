from django.db import models
from usuarios.models import Usuario
from Categorias.models import Categorias
from functools import wraps
from django.http import HttpResponseForbidden
from django import template
from django.core.exceptions import ValidationError

class Permiso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    permisos = models.ManyToManyField(Permiso, blank=True)

    def __str__(self):
        return self.nombre
    
    def delete(self, *args, **kwargs):
        # Verifica si el rol está asignado a algún usuario
        if RolEnCategoria.objects.filter(rol=self).exists():
            # Lanza una excepción si el rol está en uso
            raise ValidationError('No se puede eliminar el rol porque está asignado a un usuario.')
        super().delete(*args, **kwargs)
    
class RolEnCategoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'categoria')

    def __str__(self):
        return f"{self.usuario} - {self.categoria} - {self.rol}"


def permiso_requerido(permiso_nombre, categoria_id=None):
    def decorator(func):
        @wraps(func)
        def wrap(request, *args, **kwargs):
            usuario = request.user
            
            # Obtener los roles del usuario para la categoría actual
            roles_en_categoria = RolEnCategoria.objects.filter(usuario=usuario)
            if categoria_id:
                roles_en_categoria = roles_en_categoria.filter(categoria_id=categoria_id)
            
            permisos = Permiso.objects.none()
            for rol in roles_en_categoria:
                permisos = permisos | rol.rol.permisos.all()
            
            if not permisos.filter(nombre=permiso_nombre).exists():
                return HttpResponseForbidden("No tienes permisos suficientes.")
            
            return func(request, *args, **kwargs)
        return wrap
    return decorator



