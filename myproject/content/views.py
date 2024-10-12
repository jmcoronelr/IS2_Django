from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Content, Comentario
from .forms import ContentForm, ComentarioForm
import datetime
from Plantillas.models import Plantilla  # Importa el modelo Plantilla
from django.http import JsonResponse
import json
from .models import Content, ContentBlock
from Categorias.models import Categorias
from roles.models import RolEnCategoria, Rol
from historial.models import Historial

def content_list(request):
    # Obtener permisos necesarios
    permisos_requeridos = [
        'Contenido: Editar propio',
        'Contenido: Inactivar',
        'Contenido: Publicar',
        'Contenido: Eliminar',
        'Contenido: Ver historial',
        'Contenido: Crear'
    ]
    
    # Filtrar roles del usuario que tienen al menos uno de los permisos necesarios
    roles_con_permisos = Rol.objects.filter(
        permisos__nombre__in=permisos_requeridos
    ).values_list('id', flat=True)

    # Filtrar las categorías donde el usuario tiene estos roles
    categorias_permitidas = RolEnCategoria.objects.filter(
        usuario_id=request.user.id,
        rol_id__in=roles_con_permisos
    ).values_list('categoria_id', flat=True)

    # Filtrar los contenidos que pertenecen a esas categorías
    contents = Content.objects.filter(categoria_id__in=categorias_permitidas).order_by('created_at')

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

    # Filtrar por categoría (solo las permitidas)
    categoria = request.GET.get('categoria')
    if categoria and categoria in categorias_permitidas:
        contents = contents.filter(categoria__id=categoria)

    # Obtener solo las categorías permitidas para el usuario
    categorias = Categorias.objects.filter(id__in=categorias_permitidas)

    # Paginación
    paginator = Paginator(contents, 8)  # Muestra 8 contenidos por página
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)

    # Pasar las categorías al contexto
    return render(request, 'content/content_list.html', {
        'contents': contents,
        'categorias': categorias,  # Solo categorías permitidas
    })



def content_create_edit(request, pk=None):
    if pk:
        content = get_object_or_404(Content, pk=pk)
        accion = 'editado'
        es_nuevo = False  # Ya existe, por lo tanto, es una edición
    else:
        content = None
        accion = 'creado'
        es_nuevo = True  # No existe, por lo tanto, es creación

    plantillas = Plantilla.objects.all()

    # Filtro de categorías con permiso "Crear Contenido"
    categorias = Categorias.objects.filter(
        id__in=RolEnCategoria.objects.filter(
            usuario_id=request.user.id,
            rol_id__in=Rol.objects.filter(permisos__nombre='Contenido: Crear')  # Filtra roles con el permiso
        ).values('categoria_id'),
        estado=True
    )

    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            content = form.save(commit=False)

            plantilla_id = request.POST.get('plantilla')
            if plantilla_id:
                content.plantilla = Plantilla.objects.get(id=plantilla_id)
            else:
                content.plantilla = None

            categoria_id = request.POST.get('categoria')
            if categoria_id:
                content.categoria = Categorias.objects.get(id=categoria_id)
            else:
                content.categoria = None

            # Cambiar el estado del contenido basado en el botón presionado
            estado = request.POST.get('status')
            if estado == 'review':
                content.estado = 'review'     # Cambia el estado a 'Revision'
            elif estado == 'published':
                content.estado = 'published'    # Cambia el estado a "Publicado"
            elif estado == 'draft':
                content.estado = 'draft'        # Cambia el estado a 'Borrador'
            elif estado == 'inactive':
                content.status = 'inactive'     # Cambia el estado a 'Inactivo'

            content.save()

            block_data = json.loads(request.POST.get('block_data', '[]'))
            block_ids = []

            for block in block_data:
                bloque_id = block.get('id')

                if bloque_id:
                    content_block = ContentBlock.objects.get(id=bloque_id)
                else:
                    content_block = ContentBlock(content=content)

                content_block.block_type = block.get('type')
                content_block.content_text = block.get('content') if block.get('type') == 'texto' else None

                multimedia_file = request.FILES.get(f"multimedia-{block.get('id')}", None)
                if multimedia_file:
                    content_block.multimedia = multimedia_file

                content_block.top = block.get('top', '0px')
                content_block.left = block.get('left', '0px')
                content_block.width = block.get('width', '200px')
                content_block.height = block.get('height', '100px')
                content_block.save()

                block_ids.append(content_block.id)

            ContentBlock.objects.filter(content=content).exclude(id__in=block_ids).delete()

            Historial.objects.create(
                content=content,
                user=request.user,
                cambio=f"El contenido '{content.title}' fue {accion}.",
                version=Historial.objects.filter(content=content).count() + 1
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
        'categorias': categorias,  # Enviar las categorías filtradas
        'selected_plantilla': selected_plantilla,
        'selected_categoria': selected_categoria,
        'blocks': blocks,
        'es_nuevo': es_nuevo  # Indicador de si es creación o edición
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

def agregar_comentario(request, pk):
    contenido = get_object_or_404(Content, pk=pk)
    
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.autor = request.user
            comentario.contenido = contenido
            comentario.save()
            return redirect('content_detail', pk=contenido.pk)
    else:
        form = ComentarioForm()

    return render(request, 'comentarios/agregar_comentario.html', {'form': form, 'contenido': contenido})



def review_list(request):
    # Obtener permisos necesarios
    permisos_requeridos = [
        'Contenido: Inactivar',
        'Contenido: Publicar',
        'Contenido: Eliminar',
        'Contenido: Ver historial'
    ]
    
    # Filtrar roles del usuario que tienen al menos uno de los permisos necesarios
    roles_con_permisos = Rol.objects.filter(
        permisos__nombre__in=permisos_requeridos
    ).values_list('id', flat=True)

    # Filtrar las categorías donde el usuario tiene estos roles
    categorias_permitidas = RolEnCategoria.objects.filter(
        usuario_id=request.user.id,
        rol_id__in=roles_con_permisos
    ).values_list('categoria_id', flat=True)
    
    # Filtrar los contenidos que pertenecen a esas categorías
    contents = Content.objects.filter(categoria_id__in=categorias_permitidas).order_by('created_at')
    
    # Filtrar los estados de revision
    contents = contents.exclude(status = 'published') & contents.exclude(status = 'draft')
    
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

    # Filtrar por categoría (solo las permitidas)
    categoria = request.GET.get('categoria')
    if categoria and categoria in categorias_permitidas:
        contents = contents.filter(categoria__id=categoria)

    # Obtener solo las categorías permitidas para el usuario
    categorias = Categorias.objects.filter(id__in=categorias_permitidas)

    # Paginación
    paginator = Paginator(contents, 8)  # Muestra 8 contenidos por página
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)

    # Pasar las categorías al contexto
    return render(request, 'content/revision_list.html', {
        'contents': contents,
        'categorias': categorias,  # Solo categorías permitidas
    })
    
    
def review_detail(request, pk):
    content = get_object_or_404(Content, pk=pk)
    
    # Obtener la URL anterior o una predeterminada
    next_url = request.GET.get('next', '/content/review')

    if request.method == 'POST':
        estado = request.POST.get('status')  # Cambiado 'estado' por 'status'
        
        if estado == 'publicar':
            content.status = 'published'  # Cambia el estado a "Publicado"
        elif estado == 'rechazar':
            content.status = 'rejected'  # Cambia el estado a 'Rechazado'
        elif estado == 'borrador':
            content.status = 'draft'  # Cambia el estado a 'Borrador'
        content.save()  # Guarda los cambios

        # Redirigir de nuevo a la página de detalle o a la URL anterior
        return redirect(next_url)

    return render(request, 'content/review_detail.html', {
        'content': content,
        'next_url': next_url  # Pasar el valor de next a la plantilla
    })