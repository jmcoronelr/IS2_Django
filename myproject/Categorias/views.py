from django.shortcuts import render, redirect, get_object_or_404
from .forms import Form_Categorias
from .models import Categorias

def categoria_create(request):
    """
    Vista para crear una nueva categoría.

    Maneja la solicitud GET para mostrar el formulario vacío y la solicitud POST para 
    procesar los datos y crear una nueva instancia de Categoria.
    
    Args:
        request: El objeto HttpRequest que contiene los datos de la solicitud.
    
    Returns:
        HttpResponse: Redirige a la lista de categorías tras la creación exitosa o renderiza 
        el formulario de creación si la solicitud es GET o si el formulario no es válido.
    """
    if request.method == 'POST':
        form = Form_Categorias(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categoria_list')  # Asegúrate de tener una vista 'categoria_list' o cambia esto según tu URL
    else:
        form = Form_Categorias()

    return render(request, 'Categorias/categoria_create.html', {'form': form})


def categoria_list(request):
    """
    Vista para listar todas las categorías.

    Renderiza la plantilla 'categoria_list.html' con la lista de todas las instancias de Categoria.
    
    Args:
        request: El objeto HttpRequest que contiene los datos de la solicitud.
    
    Returns:
        HttpResponse: La respuesta HTTP con el renderizado de la plantilla.
    """
    categorias = Categorias.objects.all()  # Obtiene todas las instancias de Categorias
    return render(request, 'Categorias/categoria_list.html', {'categorias': categorias})


def categoria_edit(request, pk):
    """
    Vista para editar una categoría existente.

    Maneja la solicitud GET para mostrar el formulario precargado con los datos de la 
    categoría existente y la solicitud POST para procesar los datos y actualizar la instancia.
    
    Args:
        request: El objeto HttpRequest que contiene los datos de la solicitud.
        pk (int): Clave primaria de la categoría a editar.
    
    Returns:
        HttpResponse: Redirige a la lista de categorías tras la actualización exitosa o 
        renderiza el formulario de edición si la solicitud es GET o si el formulario no es válido.
    """
    categoria = get_object_or_404(Categorias, pk=pk)

    if request.method == 'POST':
        form = Form_Categorias(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('categoria_list')
    else:
        form = Form_Categorias(instance=categoria)

    return render(request, 'Categorias/categoria_edit.html', {'form': form})

def categoria_delete(request, pk):
    """
    Vista para eliminar una categoría existente.

    Maneja la solicitud GET para mostrar una página de confirmación de eliminación y 
    la solicitud POST para procesar la eliminación de la instancia de Categoria.
    
    Args:
        request: El objeto HttpRequest que contiene los datos de la solicitud.
        pk (int): Clave primaria de la categoría a eliminar.
    
    Returns:
        HttpResponse: Redirige a la lista de categorías tras la eliminación exitosa o 
        renderiza la página de confirmación de eliminación si la solicitud es GET.
    """
    categoria = get_object_or_404(Categorias, pk=pk)

    if request.method == 'POST':
        categoria.delete()
        return redirect('categoria_list')

    return render(request, 'Categorias/categoria_confirm_delete.html', {'categoria': categoria})