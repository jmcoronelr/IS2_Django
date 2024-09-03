from django.shortcuts import render, redirect, get_object_or_404
from .forms import Form_Categorias
from .models import Categorias

def categoria_create(request):
    if request.method == 'POST':
        form = Form_Categorias(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categoria_list')  # Asegúrate de tener una vista 'categoria_list' o cambia esto según tu URL
    else:
        form = Form_Categorias()

    return render(request, 'Categorias/categoria_form.html', {'form': form})


def categoria_list(request):
    categorias = Categorias.objects.all()  # Obtiene todas las instancias de Categorias
    return render(request, 'Categorias/categoria_list.html', {'categorias': categorias})


def categoria_edit(request, pk):
    categoria = get_object_or_404(Categorias, pk=pk)

    if request.method == 'POST':
        form = Form_Categorias(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('categoria_list')
    else:
        form = Form_Categorias(instance=categoria)

    return render(request, 'Categorias/categoria_form.html', {'form': form})

def categoria_delete(request, pk):
    categoria = get_object_or_404(Categorias, pk=pk)

    if request.method == 'POST':
        categoria.delete()
        return redirect('categoria_list')

    return render(request, 'Categorias/categoria_confirm_delete.html', {'categoria': categoria})