from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Content
from .forms import ContentForm
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
import datetime

def content_list(request):
    contents = Content.objects.all().order_by('created_at')
    
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

def content_create(request):
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('content_list')
    else:
        form = ContentForm()
    return render(request, 'content/content_form.html', {'form': form})

def content_edit(request, pk):
    content = get_object_or_404(Content, pk=pk)
    page = request.GET.get('page', 1)  # Obtiene el número de página de la URL, si no está, asume que es la página 1
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            return redirect(f'{reverse("content_list")}?page={page}')
    else:
        form = ContentForm(instance=content)
    return render(request, 'content/content_form.html', {'form': form, 'page': page})

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


