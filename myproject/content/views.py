from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Content
from .forms import ContentForm
import datetime
from Plantillas.models import Plantilla  # Importa el modelo Plantilla
from django.http import JsonResponse
import json
from .models import Content, ContentBlock
from Categorias.models import Categorias
from django.views.decorators.csrf import csrf_exempt

def content_list(request):
    contents = Content.objects.all().order_by('created_at')
    categorias = Categorias.objects.all()  # Traer todas las categorías

    # Búsqueda por título
    query = request.GET.get('q')
    if query:
        contents = contents.filter(title__icontains=query)

    # Filtrar por fecha
    fecha = request.GET.get('fecha')
    if fecha == 'today':
        contents = contents.filter(created_at__date=datetime.date.today())
    elif fecha == 'week':
        contents = contents.filter(created_at__gte=datetime.date.today() - datetime.timedelta(days=7))
    elif fecha == 'month':
        contents = contents.filter(created_at__month=datetime.date.today().month)

    # Filtrar por estado
    estado = request.GET.get('estado')
    if estado:
        contents = contents.filter(status=estado)

    # Filtrar por categoría
    categoria = request.GET.get('categoria')
    if categoria:
        contents = contents.filter(categoria__id=categoria)

    # Paginación
    paginator = Paginator(contents, 8)
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)

    # Pasar las categorías al contexto
    return render(request, 'content/content_list.html', {
        'contents': contents,
        'categorias': categorias,  # Asegúrate de pasar las categorías al template
    })

from historial.models import Historial  # Importa el modelo Historial

def content_create_edit(request, pk=None):
    if pk:
        content = get_object_or_404(Content, pk=pk)
        accion = 'editado'  # Acción para historial
    else:
        content = None
        accion = 'creado'  # Acción para historial

    plantillas = Plantilla.objects.all()
    categorias = Categorias.objects.filter(estado=True)  # Solo las categorías activas

    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            content = form.save(commit=False)
            
            # Asignar plantilla seleccionada
            plantilla_id = request.POST.get('plantilla')
            if plantilla_id:
                content.plantilla = Plantilla.objects.get(id=plantilla_id)
            else:
                content.plantilla = None

            # Asignar categoría seleccionada
            categoria_id = request.POST.get('categoria')
            if categoria_id:
                content.categoria = Categorias.objects.get(id=categoria_id)
            else:
                content.categoria = None

            content.save()

            block_data = json.loads(request.POST.get('block_data', '[]'))
            block_ids = []

            for block in block_data:
                bloque_id = block.get('id')

                # Si no hay bloque_id, creamos un nuevo bloque
                if bloque_id:
                    content_block = ContentBlock.objects.get(id=bloque_id)
                else:
                    content_block = ContentBlock(content=content)

                content_block.block_type = block.get('type')
                content_block.content_text = block.get('content') if block.get('type') == 'texto' else None

                # Manejo de archivos multimedia
                multimedia_file = request.FILES.get(f"multimedia-{block.get('id')}", None)
                if multimedia_file:
                    content_block.multimedia = multimedia_file

                content_block.top = block.get('top', '0px')
                content_block.left = block.get('left', '0px')
                content_block.width = block.get('width', '200px')
                content_block.height = block.get('height', '100px')
                content_block.save()

                block_ids.append(content_block.id)

            # Eliminar los bloques que no están en block_ids
            ContentBlock.objects.filter(content=content).exclude(id__in=block_ids).delete()

            # Registrar el cambio en el historial
            Historial.objects.create(
                content=content,
                user=request.user,  # Usuario que realizó el cambio
                cambio=f"El contenido '{content.title}' fue {accion}.",
                version=Historial.objects.filter(content=content).count() + 1  # Versión secuencial
            )

            return redirect('content_list')
    else:
        form = ContentForm(instance=content)

    blocks = ContentBlock.objects.filter(content=content) if content else []
    selected_plantilla = content.plantilla if content and content.plantilla else None
    selected_categoria = content.categoria if content and content.categoria else None

    return render(request, 'content/content_form.html', {
        'form': form,
        'plantillas': plantillas,
        'categorias': categorias,  # Enviar las categorías al template
        'selected_plantilla': selected_plantilla,
        'selected_categoria': selected_categoria,  # Enviar la categoría seleccionada
        'blocks': blocks,
    })





def content_delete(request, pk):
    content = get_object_or_404(Content, pk=pk)
    page = request.GET.get('page', 1)  # Obtiene el número de página de la URL
    if request.method == 'POST':
        content.delete()
        return redirect(f'/content/?page={page}')
    return render(request, 'content/content_confirm_delete.html', {'content': content})

def content_detail(request, pk):
    content = get_object_or_404(Content, pk=pk)
    
    # Obtén la URL anterior o utiliza una URL predeterminada (por ejemplo, '/content') si no existe 'next'
    next_url = request.GET.get('next', '/content')
    
    return render(request, 'content/content_detail.html', {
        'content': content,
        'next_url': next_url  # Pasar el valor de next a la plantilla
    })

def get_plantilla_blocks(request, plantilla_id):
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    # Acceder a los bloques asociados
    blocks = [{
        'id': bloque.id,
        'type': bloque.tipo,
        'content_text': bloque.contenido,
        'multimedia': bloque.multimedia.url if bloque.multimedia else None,
        'top': bloque.posicion_top,
        'left': bloque.posicion_left,
        'width': bloque.width,
        'height': bloque.height
    } for bloque in plantilla.bloques.all()]  # Asegúrate de usar 'bloques' si tienes related_name

    return JsonResponse({'blocks': blocks})
