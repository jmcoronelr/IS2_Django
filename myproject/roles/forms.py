from django import forms
from .models import Rol,Permiso
from Categorias.models import Categorias


class AsignarRolForm(forms.Form):
    categoria = forms.ModelChoiceField(queryset=Categorias.objects.all(), label="Categoría")
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), label="Rol")


class CrearRolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = ['nombre', 'descripcion']


class AsignarPermisoForm(forms.ModelForm):
    permisos = forms.ModelMultipleChoiceField(
        queryset=Permiso.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Permisos"
    )

    class Meta:
        model = Rol
        fields = ['permisos']  # Asegúrate de que 'permisos' sea el campo correcto para tu relación

