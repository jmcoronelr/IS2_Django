from django.db import models

class Plantilla(models.Model):
    """
    Modelo que representa una Plantilla.

    Atributos:
        descripcion (CharField): Descripción de la plantilla, con un límite de 255 caracteres.
        estado (BooleanField): Estado de la plantilla (activo/inactivo), con valor por defecto True.
    """
    descripcion = models.CharField(max_length=255)
    estado = models.BooleanField(default=True)

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto, mostrando la descripción.
        """
        return self.descripcion
