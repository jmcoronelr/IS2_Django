from django.db import models

class Categorias(models.Model):
    descripcionCorta = models.CharField(max_length=20)
    descripcionLarga = models.CharField(max_length=100)
    estado = models.BooleanField()

    def __str__(self):
        return self.title
