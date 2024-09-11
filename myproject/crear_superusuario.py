import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Asegúrate de usar el nombre correcto de tu proyecto
django.setup()

from usuarios.models import Usuario

# Crear el superusuario si no existe
if not Usuario.objects.filter(username='admin').exists():
    Usuario.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')
    print("Superusuario creado con éxito.")
else:
    print("El superusuario ya existe.")