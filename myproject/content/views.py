from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Content
from .forms import ContentForm
from django.urls import reverse
import datetime
from Plantillas.models import Plantilla  # Importa el modelo Plantilla
from django.http import JsonResponse
import json
from .models import Content, ContentBlock

def content_list(request):
    contents = Content.objects.all().order_by('created_at')
    
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
        contents = contents.filter(category__id=categoria)

    # Paginación
    paginator = Paginator(contents, 10)  # Muestra 10 contenidos por página
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)

    return render(request, 'content/content_list.html', {'contents': contents})

def content_create_edit(request, pk=None):
    if pk:
        content = get_object_or_404(Content, pk=pk)
    else:
        content = None

    plantillas = Plantilla.objects.all()

    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            content = form.save(commit=False)
            plantilla_id = request.POST.get('plantilla')
            if plantilla_id:
                content.plantilla = Plantilla.objects.get(id=plantilla_id)
            else:
                content.plantilla = None

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

            return redirect('content_list')
    else:
        form = ContentForm(instance=content)

    blocks = ContentBlock.objects.filter(content=content) if content else []
    selected_plantilla = content.plantilla if content and content.plantilla else None

    return render(request, 'content/content_form.html', {
        'form': form,
        'plantillas': plantillas,
        'selected_plantilla': selected_plantilla,
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
    return render(request, 'content/content_detail.html', {'content': content})

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
