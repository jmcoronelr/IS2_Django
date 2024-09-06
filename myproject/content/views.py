from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Content
from .forms import ContentForm
from django.urls import reverse
import datetime
from Plantillas.models import Plantilla  # Importa el modelo Plantilla
from django.http import JsonResponse

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
    plantillas = Plantilla.objects.all()  # Obtener todas las plantillas
    if request.method == 'POST':
        form = ContentForm(request.POST)
        if form.is_valid():
            # Guardar el contenido con la plantilla seleccionada
            content = form.save(commit=False)
            content.plantilla = Plantilla.objects.get(id=request.POST.get('plantilla'))  # Guardar la plantilla seleccionada
            content.save()
            return redirect('content_list')
    else:
        form = ContentForm()

    # Pasamos una plantilla vacía si no se selecciona ninguna en el formulario
    selected_plantilla = None
    if form['plantilla'].value():
        selected_plantilla = Plantilla.objects.get(id=form['plantilla'].value())

    return render(request, 'content/content_form.html', {'form': form, 'plantillas': plantillas, 'selected_plantilla': selected_plantilla})

def content_edit(request, pk):
    content = get_object_or_404(Content, pk=pk)
    plantillas = Plantilla.objects.all()  # Obtener todas las plantillas
    page = request.GET.get('page', 1)
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            return redirect(f'{reverse("content_list")}?page={page}')
    else:
        form = ContentForm(instance=content)

    # Aquí seleccionamos la plantilla que ya está guardada en el contenido
    selected_plantilla = content.plantilla if content.plantilla else None

    return render(request, 'content/content_form.html', {
        'form': form,
        'plantillas': plantillas,
        'selected_plantilla': selected_plantilla,
        'page': page
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
        'content': bloque.contenido,
        'top': bloque.posicion_top,
        'left': bloque.posicion_left,
        'width': bloque.width,
        'height': bloque.height,
    } for bloque in plantilla.bloque_set.all()]  # Usar bloque_set para obtener los bloques
    
    return JsonResponse({'blocks': blocks})
