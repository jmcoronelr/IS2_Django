# forms.py

from django import forms
from .models import Role

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'description']

    def clean_name(self):
        # Convertir el nombre a minúsculas para la validación de unicidad
        name = self.cleaned_data.get('name').lower()
        # Excluir el rol actual de la verificación
        if Role.objects.filter(name__iexact=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError("Este rol ya existe.")
        return name

