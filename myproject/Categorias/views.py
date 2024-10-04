from django.shortcuts import render, redirect, get_object_or_404
from .forms import Form_Categorias
from .models import Categorias
from django.contrib import messages

def categoria_create(request):
    """
    Vista para crear una nueva categoría.
    """
    if request.method == 'POST':
        form = Form_Categorias(request.POST)
        if form.is_valid():
            form.save()
            # Añadimos el mensaje con la tag 'category_message'
            messages.success(request, 'Categoría creada exitosamente', extra_tags='category_message')
            return redirect('categoria_list')
    else:
        form = Form_Categorias()

    return render(request, 'Categorias/categoria_create.html', {'form': form})


def categoria_list(request):
    """
    Vista para listar todas las categorías o buscar una categoría específica.
    """
    query = request.GET.get('q')
    if query:
        categorias = Categorias.objects.filter(descripcionCorta__icontains=query)
    else:
        categorias = Categorias.objects.all()
    
    return render(request, 'Categorias/categoria_list.html', {'categorias': categorias, 'query': query})


def categoria_edit(request, pk):
    """
    Vista para editar una categoría existente.
    """
    categoria = get_object_or_404(Categorias, pk=pk)

    if request.method == 'POST':
        form = Form_Categorias(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            # Añadimos el mensaje con la tag 'category_message'
            messages.success(request, 'Categoría actualizada exitosamente', extra_tags='category_message')
            return redirect('categoria_list')
    else:
        form = Form_Categorias(instance=categoria)

    return render(request, 'Categorias/categoria_edit.html', {'form': form})

from roles.models import RolEnCategoria  # Importar RolEnCategoria para verificar roles

def categoria_delete(request, pk):
    categoria = get_object_or_404(Categorias, pk=pk)
    roles_asociados = RolEnCategoria.objects.filter(categoria=categoria).exists()

    if categoria.content_set.exists():  # Verifica si hay contenidos asociados
        # Añadimos el mensaje de error con la tag 'category_message'
        messages.error(request, "No puedes eliminar esta categoría porque tiene contenidos asociados.", extra_tags='category_message')
        return redirect('categoria_list')
    
    if roles_asociados:
        # Añadir un mensaje de error si hay roles asociados
        messages.error(request, "No puedes eliminar esta categoría porque tiene roles asociados.", extra_tags='category_message')
        return redirect('categoria_list')

    if request.method == 'POST':
        categoria.delete()
        # Añadimos el mensaje de éxito con la tag 'category_message'
        messages.success(request, "Categoría eliminada con éxito.", extra_tags='category_message')
        return redirect('categoria_list')
