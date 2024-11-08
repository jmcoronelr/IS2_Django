from django.shortcuts import render, redirect
from django.urls import reverse
from content.models import Content  # Importa tu modelo de contenido
from Categorias.models import Categorias
from django.template.loader import render_to_string
from django.http import JsonResponse

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