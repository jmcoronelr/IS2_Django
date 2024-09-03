from django.shortcuts import render, get_object_or_404, redirect
from .models import Plantilla
from .forms import PlantillaForm

def plantilla_list(request):
    """
    Vista para listar todas las plantillas.

    Renderiza la plantilla 'plantilla_list.html' con la lista de todas las instancias de Plantilla.
    
    Args:
        request: El objeto HttpRequest que contiene los datos de la solicitud.
    
    Returns:
        HttpResponse: La respuesta HTTP con el renderizado de la plantilla.
    """
    plantillas = Plantilla.objects.all()
    return render(request, 'plantillas/plantilla_list.html', {'plantillas': plantillas})

def plantilla_create(request):
    """
    Vista para crear una nueva plantilla.

    Maneja la solicitud GET para mostrar el formulario vacío y la solicitud POST para 
    procesar los datos y crear una nueva instancia de Plantilla.
    
    Args:
        request: El objeto HttpRequest que contiene los datos de la solicitud.
    
    Returns:
        HttpResponse: Redirige a la lista de plantillas tras la creación exitosa o renderiza 
        el formulario de creación si la solicitud es GET o si el formulario no es válido.
    """
    if request.method == 'POST':
        form = PlantillaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('plantilla_list')
    else:
        form = PlantillaForm()
    return render(request, 'plantillas/plantilla_create.html', {'form': form})

def plantilla_edit(request, pk):
    """
    Vista para editar una plantilla existente.

    Maneja la solicitud GET para mostrar el formulario precargado con los datos de la 
    plantilla existente y la solicitud POST para procesar los datos y actualizar la instancia.
    
    Args:
        request: El objeto HttpRequest que contiene los datos de la solicitud.
        pk (int): Clave primaria de la plantilla a editar.
    
    Returns:
        HttpResponse: Redirige a la lista de plantillas tras la actualización exitosa o 
        renderiza el formulario de edición si la solicitud es GET o si el formulario no es válido.
    """
    plantilla = get_object_or_404(Plantilla, pk=pk)
    if request.method == 'POST':
        form = PlantillaForm(request.POST, instance=plantilla)
        if form.is_valid():
            form.save()
            return redirect('plantilla_list')
    else:
        form = PlantillaForm(instance=plantilla)
    return render(request, 'plantillas/plantilla_edit.html', {'form': form})

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
    return render(request, 'plantillas/plantilla_confirm_delete.html', {'plantilla': plantilla})
