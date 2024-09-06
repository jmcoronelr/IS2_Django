from django import forms
from .models import Categorias

class Form_Categorias(forms.ModelForm):
    """
    Formulario para crear o editar Categorías.

    Este formulario utiliza el modelo Categoria y permite crear o actualizar
    las instancias de Categoria con los campos 'descripcionCorta', 'descripcionLarga' y 'estado'.
    """
    class Meta:
        model = Categorias
        fields = ['descripcionCorta', 'descripcionLarga', 'estado']