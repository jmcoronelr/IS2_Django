from django.db import models
from usuarios.models import Usuario
from Categorias.models import Categorias

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
    
class RolEnCategoria(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'categoria')

    def __str__(self):
        return f"{self.usuario} - {self.categoria} - {self.rol}"





