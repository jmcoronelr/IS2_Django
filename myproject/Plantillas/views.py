from django.shortcuts import render, get_object_or_404, redirect
from .models import Plantilla
from .forms import PlantillaForm
from Plantillas.models import Plantilla
from django.core.paginator import Paginator
from django.shortcuts import render
import json
from .models import Plantilla, Bloque  # Asegúrate de importar tus modelos correctamente
from django.http import JsonResponse

def plantilla_list(request):
    """
    Vista para listar todas las plantillas
    """
    # Ordena las plantillas por fecha de creación o cualquier otro campo relevante
    plantillas = Plantilla.objects.all().order_by('-id')  # Ordena por id de forma descendente
    paginator = Paginator(plantillas, 10)  # Si tienes muchas plantillas, paginarlas
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'Plantillas/plantilla_list.html', {'plantillas': page_obj})  # Change made here
def plantilla_create(request):
    if request.method == 'POST':
        form = PlantillaForm(request.POST)
        if form.is_valid():
            # Save the plantilla instance first
            plantilla = form.save()

            # Process the blocks data from the POST request
            block_data = request.POST.get('block_data')
            if block_data:
                blocks = json.loads(block_data)

                # Save each block to the database
                for block in blocks:
                    Bloque.objects.create(
                        plantilla=plantilla,
                        tipo=block['type'],
                        contenido=block['content'],
                        posicion_top=block['top'],
                        posicion_left=block['left'],
                        width=block['width'],
                        height=block['height']
                    )

            return redirect('plantilla_list')
    else:
        form = PlantillaForm()
    return render(request, 'Plantillas/plantilla_create.html', {'form': form})



def plantilla_edit(request, pk):
    plantilla = get_object_or_404(Plantilla, pk=pk)
    bloques = Bloque.objects.filter(plantilla=plantilla)

    if request.method == 'POST':
        form = PlantillaForm(request.POST, instance=plantilla)
        if form.is_valid():
            form.save()

            # Actualizar los bloques
            Bloque.objects.filter(plantilla=plantilla).delete()  # Eliminar bloques previos
            block_data = request.POST.get('block_data')
            if block_data:
                blocks = json.loads(block_data)
                for block in blocks:
                    Bloque.objects.create(
                        plantilla=plantilla,
                        tipo=block['type'],
                        contenido=block['content'],
                        posicion_top=block['top'],
                        posicion_left=block['left'],
                        width=block['width'],
                        height=block['height']
                    )

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
