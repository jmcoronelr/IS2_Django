from django import forms
from .models import Categorias

class Form_Categorias(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = ['descripcionCorta', 'descripcionLarga', 'estado']