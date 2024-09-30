from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from PIL import Image

class UsuarioManager(BaseUserManager):
    """
    Clase que define el administrador personalizado para el modelo Usuario.
    Hereda de BaseUserManager y es responsable de crear tanto usuarios
    normales como superusuarios.

    Métodos:
    - create_user: Crea y guarda un usuario con los campos proporcionados.
    - create_superuser: Crea y guarda un superusuario con privilegios administrativos.
    """

    def create_user(self, username, email, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el nombre de usuario, correo electrónico y contraseña.

        Parámetros:
        - username (str): Nombre de usuario único.
        - email (str): Correo electrónico único.
        - password (str, opcional): Contraseña del usuario. Se encripta automáticamente.
        - extra_fields (dict): Campos adicionales opcionales para el usuario.

        Retorna:
        - user (Usuario): El objeto usuario creado.

        Lanza:
        - ValueError: Si no se proporciona un correo electrónico.
        """
        if not email:
            raise ValueError('El campo email debe ser obligatorio')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con privilegios administrativos.

        Parámetros:
        - username (str): Nombre de usuario único.
        - email (str): Correo electrónico único.
        - password (str, opcional): Contraseña del superusuario.
        - extra_fields (dict): Campos adicionales opcionales, como `is_staff` y `is_superuser`.

        Retorna:
        - superuser (Usuario): El objeto superusuario creado.

        Lanza:
        - ValueError: Si los valores de `is_staff` o `is_superuser` no son `True`.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo personalizado de usuario que extiende AbstractBaseUser y PermissionsMixin.
    Define los campos básicos para los usuarios, incluyendo nombre de usuario, email,
    nombre, apellido y estados de actividad.

    Atributos:
    - id: Identificador único del usuario.
    - username: Nombre de usuario único.
    - email: Correo electrónico único.
    - nombre: Nombre del usuario.
    - apellido: Apellido del usuario.
    - is_active: Estado de actividad del usuario.
    - is_staff: Indica si el usuario tiene permisos administrativos.

    Métodos:
    - __str__: Retorna una representación en cadena del usuario (su correo electrónico).
    """

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True, default='')
    email = models.EmailField(max_length=255, unique=True)
    apellido = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Profile(models.Model):
    """
    Falta añadir comentarios[]][][][][]
    """
    user = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    bio = models.TextField(max_length=500, blank=False)

    def __str__(self):
        return self.user.username
    
    # Ajustar tamaño de imagenes
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 100 or img.width > 100:
            new_img = (100, 100)
            img.thumbnail(new_img)
            img.save(self.avatar.path)