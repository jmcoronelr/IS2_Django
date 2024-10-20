from django import forms
from .models import Usuario, Profile

from django import forms
from .models import Usuario, Profile

class RegistroUsuarioForm(forms.ModelForm):
    """
    Formulario de registro de usuarios con confirmación de contraseña.
    """

    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'nombre', 'apellido', 'password']

    def clean(self):
        """
        Verifica que las contraseñas coincidan.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

    def clean_password(self):
        """
        Verifica que se haya proporcionado una contraseña.
        """
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('La contraseña es obligatoria.')
        return password


class UpdateUserForm(forms.ModelForm):
  """
  Falta añadir comentarios[][]][][][]
  """
  
  username = forms.CharField(max_length=100,
                               required=False,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
  email = forms.EmailField(required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control'}))
  nombre = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
  apellido = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

  class Meta:
    model = Usuario
    fields = ['username', 'email' , 'nombre', 'apellido']


class UpdateProfileForm(forms.ModelForm):
  """
  Falta añadir comentarios[]][][][][]
  """
  avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))
  bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

  class Meta:
    model = Profile
    fields = ['avatar', 'bio']


