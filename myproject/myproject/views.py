from django.shortcuts import render, redirect
from content.models import Content  # Importa tu modelo de contenido
from roles.models import Categorias, RolEnCategoria,Rol
from usuarios.models import Usuario

def home(request):
    contenidos_publicados = Content.objects.filter(status='published').order_by('created_at')

    if request.user.is_authenticated:
        return redirect('sistema')

    contenidos_con_imagenes = []
    for contenido in contenidos_publicados:
        bloques_multimedia = contenido.blocks.filter(block_type='multimedia', multimedia__isnull=False)
        # Verificar que el bloque multimedia tenga un archivo antes de intentar obtener la URL
        imagen = bloques_multimedia.first().multimedia.url if bloques_multimedia.exists() and bloques_multimedia.first().multimedia else None
        contenidos_con_imagenes.append({
            'contenido': contenido,
            'imagen': imagen,
        })

    return render(request, 'home.html', {'contenidos': contenidos_con_imagenes})

from django.shortcuts import render, redirect
from content.models import Content

def sistema(request):
    if not request.user.is_authenticated:
        return redirect('home')

    # Obtener los filtros de la URL
    letra = request.GET.get('letra', 'all')
    categoria_id = request.GET.get('categoria', 'all')
    query = request.GET.get('q', '')  # Valor de búsqueda

    # Obtener el valor del orden desde la URL (ascendente por defecto)
    order = request.GET.get('order', 'asc')

    # Verificar y asignar roles a usuarios con nombre '-'
    usuarios_sin_nombre = Usuario.objects.filter(nombre='')
    try:
        rol_suscriptor = Rol.objects.get(nombre='Suscriptor')
        categoria_none = Categorias.objects.get(descripcionLarga='None')

        # Asignar el rol 'Suscriptor' en la categoría 'None' a cada usuario sin nombre
        for usuario in usuarios_sin_nombre:
            RolEnCategoria.objects.get_or_create(
                usuario=usuario,
                categoria=categoria_none,
                defaults={'rol': rol_suscriptor}
            )
            print(f"Rol 'Suscriptor' asignado a {usuario.email} en la categoría 'None'.")
    
    except Rol.DoesNotExist:
        print("Error: No se encontró el rol 'Suscriptor'.")
    except Categorias.DoesNotExist:
        print("Error: No se encontró la categoría 'None'.")
    except Exception as e:
        print(f"Error inesperado al asignar rol: {e}")

    # Filtramos los contenidos publicados
    contenidos_publicados = Content.objects.filter(status='published')

    # Filtrar por letra si se ha seleccionado
    if letra != 'all':
        contenidos_publicados = contenidos_publicados.filter(title__istartswith=letra)
    
    # Filtrar por categoría si se ha seleccionado
    if categoria_id and categoria_id != 'all':
        contenidos_publicados = contenidos_publicados.filter(categoria__id=categoria_id)

    # Filtrar por búsqueda dinámica (solo en el título)
    if query:
        contenidos_publicados = contenidos_publicados.filter(title__icontains=query)

    # Aplicar el orden a los contenidos
    if order == 'desc':
        contenidos_publicados = contenidos_publicados.order_by('-title')
    else:
        contenidos_publicados = contenidos_publicados.order_by('title')

    # Obtener todas las categorías
    categorias = Categorias.objects.all()

    # Agregar lógica para extraer las imágenes multimedia de los bloques
    contenidos_con_imagenes = []
    for contenido in contenidos_publicados:
        bloques_multimedia = contenido.blocks.filter(block_type='multimedia', multimedia__isnull=False)
        # Seleccionar la primera imagen si hay alguna
        imagen = bloques_multimedia.first().multimedia.url if bloques_multimedia.exists() and bloques_multimedia.first().multimedia else None
        contenidos_con_imagenes.append({
            'contenido': contenido,
            'imagen': imagen,
        })

    return render(request, 'sistema.html', {
        'contenidos': contenidos_con_imagenes,
        'letra_seleccionada': letra,
        'categorias': categorias,
    })