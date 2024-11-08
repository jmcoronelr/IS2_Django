from django.db import models
from Plantillas.models import Plantilla  # Importa el modelo de Plantilla
from Categorias.models import Categorias
from django.conf import settings
from django.db import models
from django.utils import timezone

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
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    plantilla = models.ForeignKey(Plantilla, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    revision_started_at = models.DateTimeField(null=True, blank=True)
    revision_ended_at = models.DateTimeField(null=True, blank=True)
    published_started_at = models.DateField(null=True, blank=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    numero_visitas = models.PositiveIntegerField(default=0)
    shared_count = models.IntegerField(default=0)
    inactivated_at = models.DateTimeField(null=True, blank=True)

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

class Comentario(models.Model):
    contenido = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comentario de {self.autor} en {self.contenido}'

class UserInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='interactions')
    liked = models.BooleanField(default=False)
    disliked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {self.content.title} - {"Liked" if self.liked else "Disliked" if self.disliked else "None"}'