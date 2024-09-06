import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from roles.models import Permiso

# Crea una lista de permisos con sus descripciones
permisos = [
    {'nombre': 'compartir_contenido', 'descripcion': 'Permite compartir contenidos del sitio.'},
    {'nombre': 'comentar_contenido', 'descripcion': 'Permite realizar comentarios en los contenidos.'},
    {'nombre': 'crear_contenido', 'descripcion': 'Permite crear nuevos contenidos.'},
    {'nombre': 'editar', 'descripcion': 'Permite editar contenidos.'},
    {'nombre': 'publicar_contenido', 'descripcion': 'Permite publicar contenidos en el sitio web.'},
    {'nombre': 'administrar_sitio', 'descripcion': 'Permite administrar todas las funcionalidades del sistema (gestión de usuarios, permisos, configuración del sitio, etc.).'},
]

# Inserta los permisos en la base de datos
for permiso in permisos:
    p, created = Permiso.objects.get_or_create(
        nombre=permiso['nombre'],
        defaults={'descripcion': permiso['descripcion']}
    )
    if created:
        print(f'Permiso creado: {p.nombre}')
    else:
        print(f'Permiso ya existe: {p.nombre}')
