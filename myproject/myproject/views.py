from django.shortcuts import render, redirect
from django.urls import reverse
from content.models import Content  # Importa tu modelo de contenido
from Categorias.models import Categorias
from django.template.loader import render_to_string
from django.http import JsonResponse

def home(request):
    if request.user.is_authenticated:
        return redirect('sistema')
    return render(request, 'home.html')

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

    # Verificar si la solicitud es AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Devolver el HTML completo que estaba en la plantilla parcial, pero como una cadena dentro del JSON
        html = ''
        for contenido in contenidos_publicados:
            html += f'''
                <div class="content-item">
                   <!-- <div class="content-category">{contenido.categoria.descripcionLarga}</div> -->
                    <div class="content-image">
                        <span>Sin imagen</span>
                    </div>
                    <div class="content-details">
                        <h3>{contenido.title}</h3>
                        <div class="description">{contenido.description}</div>
                        <a href="#">Ver más</a>
                    </div>
                </div>
            '''
        return JsonResponse({'html': html})

    return render(request, 'sistema.html', {
        'contenidos': contenidos_publicados,
        'letra_seleccionada': letra,
        'categorias': categorias,
    })