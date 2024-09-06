from django.db import models

class Plantilla(models.Model):
    descripcion = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

class Bloque(models.Model):
    plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE, related_name='bloques')
    tipo = models.CharField(max_length=50)  # 'texto' o 'multimedia'
    contenido = models.TextField()
    posicion_top = models.CharField(max_length=50)
    posicion_left = models.CharField(max_length=50)
    width = models.CharField(max_length=50, blank=True, default='200px')
    height = models.CharField(max_length=50, blank=True, default='100px')   

    def __str__(self):
        return f'{self.tipo} - {self.contenido[:30]}'

