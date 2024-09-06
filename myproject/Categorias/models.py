from django.db import models

class Categorias(models.Model):
    """
    Modelo que representa una Categoría.

    Atributos:
        descripcionCorta (CharField): Descripción corta de la categoría, con un límite de 255 caracteres.
        descripcionLarga (TextField): Descripción larga de la categoría.
        estado (BooleanField): Estado de la categoría (activo/inactivo), con valor por defecto True.
    """
    descripcionCorta = models.CharField(max_length=20)
    descripcionLarga = models.CharField(max_length=100)
    estado = models.BooleanField()

    def __str__(self):
        """
        Devuelve una representación en cadena del objeto, mostrando la descripción corta.
        """
        return self.descripcionLarga
