from django import forms
from .models import Usuario, Rol

class RegistroUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'nombre', 'apellido', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('La contraseña es obligatoria.')
        return password


class AsignarRolForm(forms.Form):
    usuario = forms.ModelChoiceField(queryset=Usuario.objects.all())
    rol = forms.ModelChoiceField(queryset=Rol.objects.all())
