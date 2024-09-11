from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

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
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Rol(models.Model):
    """
    Modelo que define un rol en el sistema. Cada rol tiene un nombre único y una
    descripción opcional.

    Atributos:
    - nombre: Nombre único del rol.
    - descripcion: Descripción opcional del rol.

    Métodos:
    - __str__: Retorna el nombre del rol.
    """

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Permiso(models.Model):
    """
    Modelo que define un permiso en el sistema. Cada permiso tiene un nombre único y una
    descripción opcional.

    Atributos:
    - nombre: Nombre único del permiso.
    - descripcion: Descripción opcional del permiso.

    Métodos:
    - __str__: Retorna el nombre del permiso.
    """

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class UsuarioRol(models.Model):
    """
    Modelo intermedio para establecer la relación entre el modelo Usuario y el modelo Rol.
    Representa una relación muchos a muchos.

    Atributos:
    - usuario: Relación con el modelo Usuario.
    - rol: Relación con el modelo Rol.

    Meta:
    - unique_together: Garantiza que cada combinación de usuario y rol sea única.
    """

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'rol')

class RolPermiso(models.Model):
    """
    Modelo intermedio para establecer la relación entre el modelo Rol y el modelo Permiso.
    Representa una relación muchos a muchos.

    Atributos:
    - rol: Relación con el modelo Rol.
    - permiso: Relación con el modelo Permiso.

    Meta:
    - unique_together: Garantiza que cada combinación de rol y permiso sea única.
    """

    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('rol', 'permiso')


