import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from roles.models import Rol, Permiso

# Define los roles con los permisos asociados por nombre
roles_data = [
    {'nombre': 'Suscriptor', 
     'descripcion': 'Puede ver, comentar y compartir contenido.', 
     'permisos': [
         {'nombre': 'Contenido: Compartir'},
         {'nombre': 'Contenido: Comentar'}
        ]
    },
    {'nombre': 'Autor', 
     'descripcion': 'Puede crear, editar y eliminar su propio contenido.', 
     'permisos': [
         {'nombre': 'Contenido: Compartir'},
         {'nombre': 'Contenido: Comentar'},
         {'nombre': 'Contenido: Crear'},
         {'nombre': 'Contenido: Editar propio'},
         {'nombre': 'Contenido: Eliminar'},
         {'nombre': 'Contenido: Ver historial'}
        ]
    },
    {'nombre': 'Editor', 
     'descripcion': 'Puede gestionar y editar todo el contenido de su categoría.', 
     'permisos': [
         {'nombre': 'Contenido: Compartir'},
         {'nombre': 'Contenido: Comentar'},
         {'nombre': 'Contenido: Crear'},
         {'nombre': 'Contenido: Editar propio'},
         {'nombre': 'Contenido: Eliminar'},
         {'nombre': 'Contenido: Ver historial'},
         {'nombre': 'Contenido: Mandar a revisión'}
        ]
    },
    {'nombre': 'Publicador', 
     'descripcion': 'Puede gestionar, editar y publicar contenido de su categoria.', 
     'permisos': [
         {'nombre': 'Contenido: Compartir'},
         {'nombre': 'Contenido: Comentar'},
         {'nombre': 'Contenido: Crear'},
         {'nombre': 'Contenido: Editar propio'},
         {'nombre': 'Contenido: Eliminar'},
         {'nombre': 'Contenido: Ver historial'},
         {'nombre': 'Contenido: Mandar a revisión'},
         {'nombre': 'Contenido: Publicar'},
         {'nombre': 'Contenido: Rechazar'}
        ]
    },
]


for rol_data in roles_data:
    # Crear o obtener el rol
    rol_obj, created = Rol.objects.get_or_create(
        nombre=rol_data['nombre'],
        defaults={'descripcion': rol_data['descripcion']}
    )
    
    # Buscar y asociar permisos existentes
    permisos_data = rol_data['permisos']
    for permiso_data in permisos_data:
        try:
            # Accede al nombre del permiso correctamente
            permiso_obj = Permiso.objects.get(nombre=permiso_data['nombre'])
            rol_obj.permisos.add(permiso_obj)  # Agrega la relación a la tabla intermedia
        except Permiso.DoesNotExist:
            print(f"Permiso no encontrado: {permiso_data['nombre']}")
    
    rol_obj.save()
    if created:
        print(f"Rol creado: {rol_obj.nombre}")
    else:
        print(f"Rol actualizado: {rol_obj.nombre}")
