from django.shortcuts import render, get_object_or_404, redirect
from .models import Plantilla
from .forms import PlantillaForm
from Plantillas.models import Plantilla
from django.core.paginator import Paginator
from django.shortcuts import render
import json
from .models import Plantilla, Bloque  # Asegúrate de importar tus modelos correctamente
from django.http import JsonResponse
from django.db.models import Q  # Import necesario para realizar búsquedas

def plantilla_list(request):
    """
    Vista para listar todas las plantillas
    """
    query = request.GET.get('q')  # Obtener el valor del campo de búsqueda (si existe)
    
    if query:
        # Filtrar plantillas que coincidan con la búsqueda (en la descripción)
        plantillas = Plantilla.objects.filter(Q(descripcion__icontains=query)).order_by('-id')
    else:
        # Si no hay búsqueda, obtener todas las plantillas
        plantillas = Plantilla.objects.all().order_by('-id')
    
    paginator = Paginator(plantillas, 10)  # Paginación
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'Plantillas/plantilla_list.html', {'plantillas': page_obj})

def plantilla_create(request):
    if request.method == 'POST':
        form = PlantillaForm(request.POST, request.FILES)
        if form.is_valid():
            plantilla = form.save()

            block_data = request.POST.get('block_data')
            if block_data:
                blocks = json.loads(block_data)
                for block in blocks:
                    bloque = Bloque(
                        plantilla=plantilla,
                        tipo=block['type'],
                        contenido=block['content'] if block['type'] == 'texto' else '',
                        posicion_top=block['top'],
                        posicion_left=block['left'],
                        width=block['width'],
                        height=block['height']
                    )
                    if block['type'] == 'multimedia' and 'multimedia' in request.FILES:
                        bloque.multimedia = request.FILES['multimedia']
                    bloque.save()

            return redirect('plantilla_list')
    else:
        form = PlantillaForm()

    return render(request, 'Plantillas/plantilla_create.html', {'form': form})


def plantilla_edit(request, pk):
    plantilla = get_object_or_404(Plantilla, pk=pk)
    bloques = Bloque.objects.filter(plantilla=plantilla)

    # Update the blocks to indicate their file types
    for bloque in bloques:
        if bloque.tipo == 'multimedia' and bloque.multimedia:
            file_url = bloque.multimedia.url
            if file_url.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                bloque.file_type = 'image'
            elif file_url.endswith(('.mp3', '.wav')):
                bloque.file_type = 'audio'
            elif file_url.endswith(('.mp4', '.webm', '.avi')):
                bloque.file_type = 'video'

    if request.method == 'POST':
        form = PlantillaForm(request.POST, request.FILES, instance=plantilla)
        if form.is_valid():
            form.save()

            block_data = request.POST.get('block_data')
            block_ids = []
            if block_data:
                blocks = json.loads(block_data)

                for block in blocks:
                    bloque_id = block.get('id')

                    # Check if the block already exists
                    if bloque_id:
                        bloque = Bloque.objects.get(id=bloque_id)
                    else:
                        bloque = Bloque(plantilla=plantilla)

                    # Update block positions, size, and content
                    bloque.tipo = block['type']
                    bloque.posicion_top = block['top']
                    bloque.posicion_left = block['left']
                    bloque.width = block['width']
                    bloque.height = block['height']

                    # If it's a multimedia block, handle the file upload
                    if block['type'] == 'texto':
                        bloque.contenido = block['content']  # Mantén el contenido del texto
                    elif block['type'] == 'multimedia':
                        multimedia_field_name = f'multimedia-{block.get("id") or "new"}'
                        # Check if a new file has been uploaded
                        if multimedia_field_name in request.FILES:
                            bloque.multimedia = request.FILES['multimedia_field_name']
                        # Otherwise, keep the existing file if no new one is uploaded
                        elif bloque.multimedia:
                            bloque.multimedia = bloque.multimedia
                        else:
                            bloque.multimedia=None

                    bloque.save()

                    block_ids.append(bloque.id)

            Bloque.objects.filter(plantilla=plantilla).exclude(id__in=block_ids).delete()

            return redirect('plantilla_list')
        
        

    else:
        form = PlantillaForm(instance=plantilla)

    return render(request, 'Plantillas/plantilla_edit.html', {'form': form, 'bloques': bloques})

def plantilla_delete(request, pk):
    """
    Vista para eliminar una plantilla existente.

    Maneja la solicitud GET para mostrar una página de confirmación de eliminación y 
    la solicitud POST para procesar la eliminación de la instancia de Plantilla.
    
    Args:
        request: El objeto HttpRequest que contiene los datos de la solicitud.
        pk (int): Clave primaria de la plantilla a eliminar.
    
    Returns:
        HttpResponse: Redirige a la lista de plantillas tras la eliminación exitosa o 
        renderiza la página de confirmación de eliminación si la solicitud es GET.
    """
    plantilla = get_object_or_404(Plantilla, pk=pk)
    if request.method == 'POST':
        plantilla.delete()
        return redirect('plantilla_list')
    return render(request, 'Plantillas/plantilla_confirm_delete.html', {'plantilla': plantilla})

def get_plantilla_blocks(request, plantilla_id):
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    # Acceder a los bloques asociados
    blocks = [{
        'content': bloque.contenido,
        'top': bloque.posicion_top,
        'left': bloque.posicion_left,
        'width': bloque.width,
        'height': bloque.height,
    } for bloque in plantilla.bloques.all()]
    
    return JsonResponse({'blocks': blocks})
