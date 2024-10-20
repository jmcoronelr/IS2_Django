from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Backend de autenticación que permite a los usuarios iniciar sesión
    tanto con el correo electrónico como con el nombre de usuario.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Buscar al usuario ya sea por nombre de usuario o correo electrónico
            user = User.objects.get(username=username) if '@' not in username else User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        
        # Verificar la contraseña
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
