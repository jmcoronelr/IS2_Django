from django.db import models

class Tarea(models.Model):
    ESTADOS = [
        ('borrador', 'Borrador'),
        ('revision', 'Revisión'),
        ('publicado', 'Publicado'),
        ('rechazado', 'Rechazado'),
    ]

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='borrador')

    def __str__(self):
        return self.titulo
