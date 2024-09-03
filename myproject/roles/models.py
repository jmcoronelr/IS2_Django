from django.db import models
from django.core.exceptions import ValidationError

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  # El rol debe ser único
    description = models.TextField(blank=True, null=True)

    def clean(self):
    # Excluir el rol actual de la verificación
        if Role.objects.filter(name__iexact=self.name).exclude(id=self.id).exists():
            raise ValidationError("Este rol ya existe.")
