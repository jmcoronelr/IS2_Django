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
    plantilla = models.ForeignKey(Plantilla, on_delete=models.SET_NULL, null=True, blank=True)  # Relación con Plantilla
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ContentBlock(models.Model):
    BLOCK_TYPE_CHOICES = [
        ('texto', 'Texto'),
        ('multimedia', 'Multimedia'),
    ]

    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='blocks')
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES)
    content_text = models.TextField(blank=True, null=True)  # Solo para bloques de texto
    multimedia = models.FileField(upload_to='uploads/', null=True, blank=True)  # Para bloques de multimedia
    top = models.CharField(max_length=10, default='0px')
    left = models.CharField(max_length=10, default='0px')
    width = models.CharField(max_length=10, default='200px')
    height = models.CharField(max_length=10, default='100px')

    def __str__(self):
        return f"{self.block_type} - {self.content.title}"
