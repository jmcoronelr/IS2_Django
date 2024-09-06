from django.db import models
from Plantillas.models import Plantilla  # Importa el modelo de Plantilla

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Content(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('review', 'En Revisión'),
        ('published', 'Publicado'),
        ('rejected', 'Rechazado'),
        ('inactive', 'Inactivo'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    plantilla = models.ForeignKey(Plantilla, on_delete=models.SET_NULL, null=True, blank=True)  # Agrega esta línea
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
