from django import forms
from .models import Usuario

class RegistroUsuarioForm(forms.ModelForm):
    """
    Formulario de registro de usuarios basado en un ModelForm.
    Este formulario permite la creación de un nuevo usuario mediante
    los campos especificados en el modelo `Usuario`.

    Atributos:
    - password: Campo de contraseña que utiliza un widget de tipo `PasswordInput` 
      para ocultar la entrada de texto.

    Meta:
    - model: Especifica que el formulario está asociado con el modelo `Usuario`.
    - fields: Define los campos que serán mostrados en el formulario: 
      `username`, `email`, `nombre`, `apellido`, y `password`.

    Métodos:
    - clean_password: Valida que la contraseña no esté vacía. 
      Si no se proporciona una contraseña, se lanza una `ValidationError`.
    """

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'nombre', 'apellido', 'password']

    def clean_password(self):
        """
        Verifica si el campo de contraseña ha sido completado correctamente.

        Retorna:
        - password (str): La contraseña validada.

        Lanza:
        - forms.ValidationError: Si no se proporciona ninguna contraseña.
        """
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError('La contraseña es obligatoria.')
        return password


