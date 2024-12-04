from django.db import models
from django.conf import settings
from content.models import Content

class Historial(models.Model):
    version = models.IntegerField(default=1)
    content = models.ForeignKey(Content, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    cambio = models.TextField()
    accion_detalle = models.TextField(null=True, blank=True)  # Nuevo campo

    def __str__(self):
        return f"{self.content.title} - {self.version}"
