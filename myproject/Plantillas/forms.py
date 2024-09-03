from django import forms
from .models import Plantilla

class PlantillaForm(forms.ModelForm):
    """
    Formulario para crear o editar Plantillas.

    Este formulario utiliza el modelo Plantilla y permite crear o actualizar
    las instancias de Plantilla con los campos 'descripcion' y 'estado'.
    """
    class Meta:
        model = Plantilla
        fields = ['descripcion', 'estado']
