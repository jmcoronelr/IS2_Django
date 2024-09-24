import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from roles.models import Permiso

# Crea una lista de permisos con sus descripciones
permisos = [
    {'nombre': 'Compartir contenido', 'descripcion': 'Permite compartir contenidos del sitio.'},
    {'nombre': 'Comentar contenido', 'descripcion': 'Permite realizar comentarios en los contenidos.'},
    {'nombre': 'Crear contenido', 'descripcion': 'Permite crear nuevos contenidos.'},
    {'nombre': 'Editar contenido propio', 'descripcion': 'Permite al usuario editar sus propios contenidos.'},
    {'nombre': 'Editar contenido otros', 'descripcion': 'Permite al usuario editar contenidos de otros autores.'},
    {'nombre': 'Publicar contenido', 'descripcion': 'Permite publicar contenidos en el sitio web.'},
    {'nombre': 'Ver usuarios', 'descripcion': 'Permite visualizar la lista de usuarios registrados en el sistema.'},
    {'nombre': 'Actualizar usuarios', 'descripcion': 'Permite modificar la información de los usuarios existentes.'},
    {'nombre': 'Eliminar usuarios', 'descripcion': 'Permite eliminar usuarios del sistema de manera permanente.'},
    {'nombre': 'Crear roles', 'descripcion': 'Permite crear nuevos roles.'},
    {'nombre': 'Asignar roles', 'descripcion': 'Permite asignar roles a los usuarios del sistema.'},
    {'nombre': 'Editar roles', 'descripcion': 'Permite modificar los permisos y detalles de roles existentes en el sistema.'},
    {'nombre': 'Eliminar roles', 'descripcion': 'Permite eliminar roles que no estén asignados a ningún usuario en el sistema.'},
    {'nombre': 'Crear categorias', 'descripcion': 'Permite crear nuevas categorías para clasificar los contenidos del sitio.'},
    {'nombre': 'Modificar categorias', 'descripcion': 'Permite modificar los detalles de las categorías existentes, como su nombre o descripción.'},
    {'nombre': 'Inactivar categorias', 'descripcion': 'Permite marcar categorías como inactivas, lo que impide que se asocien a nuevos contenidos pero las mantiene en el sistema.'},
    {'nombre': 'Eliminar categorias', 'descripcion': 'Permite eliminar categorías que ya no son necesarias y no están asociadas a ningún contenido.'},
    {'nombre': 'Ver historial', 'descripcion': 'Permite visualizar el historial de modificaciones realizadas sobre los contenidos.'},
    {'nombre': 'Inactivar contenido', 'descripcion': 'Permite marcar un contenido como inactivo, lo que lo oculta de la vista pública sin eliminarlo del sistema.'},
    {'nombre': 'Configurar atributos del sitio', 'descripcion': 'Permite configurar atributos generales del sitio, como el nombre, el logo y la descripción.'},
    {'nombre': 'Generar reportes: Categoria mas compartida', 'descripcion': 'Permite generar un reporte sobre las categorías más compartidas por los usuarios.'},
    {'nombre': 'Generar reportes: Usuarios con mayor numero creaciones', 'descripcion': 'Permite generar un reporte sobre los usuarios que han creado más contenidos en el sistema.'},
    {'nombre': 'Generar reportes: Usuarios con mayor numero ediciones', 'descripcion': 'Permite generar un reporte sobre los usuarios que han editado más contenidos en el sistema.'},
    {'nombre': 'Generar reportes: Usuarios con mayor numero publicaciones', 'descripcion': 'Permite generar un reporte sobre los usuarios que han publicado más contenidos en el sistema.'},
    {'nombre': 'Generar reportes: Cantidad de publicaciones aprobadas', 'descripcion': 'Permite generar un reporte sobre la cantidad de publicaciones que han sido aprobadas en el sistema.'},
    {'nombre': 'Generar reportes: Publicaciones mas comentadas', 'descripcion': 'Permite generar un reporte sobre las publicaciones que han recibido más comentarios.'},
    {'nombre': 'Generar reportes: Cantidad personas que accedieron a un articulo', 'descripcion': 'Permite generar un reporte sobre cuántas personas han accedido a un artículo específico.'},
    {'nombre': 'Generar reportes: Cantidad de likes por cada articulo', 'descripcion': 'Permite generar un reporte sobre la cantidad de "likes" recibidos por cada artículo.'},
    {'nombre': 'Generar reportes: Cinco articulos mas populares', 'descripcion': 'Permite generar un reporte sobre los cinco artículos más populares en el sistema.'},
    {'nombre': 'Generar reportes: Cantidad articulos publicados', 'descripcion': 'Permite generar un reporte sobre la cantidad de artículos publicados en el sistema en un período determinado.'},
    {'nombre': 'Generar reportes: Cantidad de articulos redactados y tiempo promedio de revision', 'descripcion': 'Permite generar un reporte sobre la cantidad de artículos redactados y el tiempo promedio que tomaron para ser revisados.'},
    {'nombre': 'Generar reportes: Cantidad de articulos inactivos', 'descripcion': 'Permite generar un reporte sobre la cantidad de artículos que han sido marcados como inactivos en el sistema.'},
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
