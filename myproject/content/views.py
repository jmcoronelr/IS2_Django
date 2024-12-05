from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .forms import ContentForm, ComentarioForm
import datetime
from Plantillas.models import Plantilla  # Importa el modelo Plantilla
from django.http import JsonResponse
import json
from .models import Content, ContentBlock
from historial.models import Historial
from Categorias.models import Categorias
from roles.models import RolEnCategoria, Rol
from django.contrib import messages
from content.models import UserInteraction
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail

import json

def content_list(request):
    """
    Muestra una lista de contenidos, con la opción de filtrarlos por permisos, estado, categoría, fecha y título.
    
    Si el usuario es superusuario, se muestran todos los contenidos. Los usuarios regulares solo ven los contenidos 
    que corresponden a las categorías en las que tienen roles con permisos específicos.
    También se incluye la opción de paginar los resultados.
    """
    if request.user.is_superuser:
        contents = Content.objects.all().order_by('created_at')
        categorias = Categorias.objects.all()
    else:
        permisos_requeridos = [
            'Contenido: Editar', 'Contenido: Inactivar', 'Contenido: Publicar',
            'Contenido: Eliminar', 'Contenido: Ver historial', 'Contenido: Crear'
        ]
        roles_con_permisos = Rol.objects.filter(permisos__nombre__in=permisos_requeridos).values_list('id', flat=True)
        categorias_permitidas = RolEnCategoria.objects.filter(usuario_id=request.user.id, rol_id__in=roles_con_permisos).values_list('categoria_id', flat=True)
        contents = Content.objects.filter(categoria_id__in=categorias_permitidas).order_by('created_at')
        categorias = Categorias.objects.filter(id__in=categorias_permitidas)

    # Obtener el valor de la pestaña activa (default 'mine')
    tab = request.GET.get('tab', 'mine')

    # Filtrar por autor
    if tab == 'mine':
        contents= contents.filter(autor=request.user)
    else:
        contents = contents.exclude(autor=request.user)

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

    estado = request.GET.get('estado')
    if estado:
        contents = contents.filter(status=estado)

    categoria = request.GET.get('categoria')
    if not request.user.is_superuser and categoria and categoria in categorias_permitidas:
        contents = contents.filter(categoria__id=categoria)

    paginator = Paginator(contents, 8)
    page_number = request.GET.get('page')
    contents = paginator.get_page(page_number)

    return render(request, 'content/content_list.html', {
        'contents': contents,
        'categorias': categorias,
        'tab': tab,  # Pasar la pestaña activa al contexto
    })

def content_create_edit(request, pk=None):
    """
    Crea o edita un contenido.

    Si se proporciona una clave primaria (pk), se edita el contenido existente; de lo contrario, se crea uno nuevo.
    Actualiza el historial con detalles específicos de los cambios realizados.
    """
    if pk:
        content = get_object_or_404(Content, pk=pk)
        accion = 'editado'
        old_title = content.title
        old_description = content.description
        old_status = content.status
        old_categoria = content.categoria
        old_plantilla = content.plantilla  # Guardar plantilla anterior
        es_nuevo = False
        content.status = 'review'

        if content.revision_started_at is None:
            content.revision_started_at = timezone.now()
    else:
        content = None
        accion = 'creado'
        old_title = None
        old_description = None
        old_status = None
        old_categoria = None
        old_plantilla = None
        es_nuevo = True

    plantillas = Plantilla.objects.all()

    if request.user.is_superuser:
        categorias = Categorias.objects.filter(estado=True)
    else:
        categorias = Categorias.objects.filter(
            id__in=RolEnCategoria.objects.filter(
                usuario_id=request.user.id,
                rol_id__in=Rol.objects.filter(permisos__nombre='Contenido: Crear')
            ).values('categoria_id'),
            estado=True
        )

    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            content = form.save(commit=False)

            if not pk:
                content.autor = request.user

            plantilla_id = request.POST.get('plantilla')
            if plantilla_id:
                nueva_plantilla = Plantilla.objects.get(id=plantilla_id)
                content.plantilla = nueva_plantilla
            else:
                nueva_plantilla = None
                content.plantilla = None

            categoria_id = request.POST.get('categoria')
            if categoria_id:
                content.categoria = Categorias.objects.get(id=categoria_id)
            else:
                content.categoria = None

            new_status = content.status
            estado = request.POST.get('status')
            if estado == 'review':
                content.estado = 'review'
            elif estado == 'published':
                content.estado = 'published'
            elif estado == 'draft':
                content.estado = 'draft'
            elif estado == 'inactive':
                content.status = 'inactive'

            content.save()

            if old_status and old_status != new_status:
                send_mail(
                    subject=f'Actualización de estado para "{content.title}"',
                    message=f'Hola {content.autor.username},\n\nTu contenido "{content.title}" ha cambiado su estado de "{old_status}" a "{new_status}".',
                    from_email='tu_correo@gmail.com',
                    recipient_list=[content.autor.email],
                    fail_silently=False,
                )

            block_data = json.loads(request.POST.get('block_data', '[]'))
            block_ids = []
            detalles_cambios = []

            # Obtener los bloques existentes antes de guardar
            existing_blocks = ContentBlock.objects.filter(content=content)
            existing_blocks_dict = {str(block.id): block for block in existing_blocks}

            for block in block_data:
                bloque_id = block.get('id')
                if bloque_id and bloque_id in existing_blocks_dict:
                    # Bloque existente: comprobar cambios
                    content_block = existing_blocks_dict[bloque_id]
                    if content_block.block_type != block.get('type'):
                        detalles_cambios.append("Se cambió el tipo de un bloque.")
                    if content_block.content_text != block.get('content'):
                        detalles_cambios.append("Se modificó el contenido de un bloque.")
                    multimedia_file = request.FILES.get(f"multimedia-{block.get('id')}", None)
                    if multimedia_file:
                        content_block.multimedia = multimedia_file
                        detalles_cambios.append("Se actualizó el archivo multimedia de un bloque.")
                    content_block.block_type = block.get('type')
                    content_block.content_text = block.get('content')
                    content_block.top = block.get('top', '0px')
                    content_block.left = block.get('left', '0px')
                    content_block.width = block.get('width', '200px')
                    content_block.height = block.get('height', '100px')
                    content_block.save()
                else:
                    # Nuevo bloque
                    content_block = ContentBlock(
                        content=content,
                        block_type=block.get('type'),
                        content_text=block.get('content') if block.get('type') == 'texto' else None,
                        top=block.get('top', '0px'),
                        left=block.get('left', '0px'),
                        width=block.get('width', '200px'),
                        height=block.get('height', '100px'),
                        multimedia=request.FILES.get(f"multimedia", None) if block.get('type') == 'multimedia' else None,
                    )
                    content_block.save()
                    detalles_cambios.append("Se añadió un nuevo bloque.")
                block_ids.append(content_block.id)

            # Detectar bloques eliminados
            deleted_blocks = existing_blocks.exclude(id__in=block_ids)
            if deleted_blocks.exists():
                detalles_cambios.append("Se eliminaron bloques de contenido.")

            deleted_blocks.delete()

            # Registrar cambios en el historial
            if old_title and old_title != content.title:
                detalles_cambios.append("Se cambió el título del contenido.")
            if old_description and old_description != content.description:
                detalles_cambios.append("Se actualizó la descripción del contenido.")
            if old_categoria and old_categoria != content.categoria:
                detalles_cambios.append("Se cambió la categoría del contenido.")
            if old_plantilla != nueva_plantilla:
                if nueva_plantilla:
                    detalles_cambios.append(f"Se seleccionó la plantilla '{nueva_plantilla.descripcion}'.")
                else:
                    detalles_cambios.append("Se eliminó la plantilla seleccionada.")

            Historial.objects.create(
                content=content,
                user=request.user,
                cambio=f"El contenido '{content.title}' fue {accion}.",
                version=Historial.objects.filter(content=content).count() + 1,
                accion_detalle="\n".join(detalles_cambios)
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
        'categorias': categorias,
        'selected_plantilla': selected_plantilla,
        'selected_categoria': selected_categoria,
        'blocks': blocks,
        'es_nuevo': es_nuevo
    })







def content_delete(request, pk):
    """
    Elimina un contenido seleccionado.
    
    Permite eliminar un contenido confirmando la acción con el usuario.
    """
    content = get_object_or_404(Content, pk=pk)
    page = request.GET.get('page', 1)
    if request.method == 'POST':
        content.delete()
        return redirect(f'/content/?page={page}')
    return render(request, 'content/content_confirm_delete.html', {'content': content})


def content_detail(request, pk):
    """
    Muestra los detalles de un contenido específico, incluidas las interacciones del usuario.
    
    También permite agregar comentarios al contenido y verificar si el usuario ha dado like o dislike.
    """
    content = get_object_or_404(Content, pk=pk)
    next_url = request.GET.get('next', '/content')
    
    user_interaction = None
    liked = False
    disliked = False

    # Verificar si la solicitud anterior fue un comentario para evitar duplicar la visita
    if request.method == 'GET' and not request.session.pop('avoid_double_count', False):
        # Incrementar el número total de visitas
        content.numero_visitas += 1
        content.save()

    if request.user.is_authenticated:
        user_interaction = UserInteraction.objects.filter(user=request.user, content=content).first()
        if user_interaction:
            liked = user_interaction.liked
            disliked = user_interaction.disliked

    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.autor = request.user
            comentario.contenido = content
            comentario.save()
            # Establecer un marcador temporal en la sesión para evitar el conteo doble de visitas
            request.session['avoid_double_count'] = True
            return redirect('content_detail', pk=content.pk)
    else:
        form = ComentarioForm()

    # Obtiene la URL completa del contenido
    content_url = request.build_absolute_uri()

    return render(request, 'content/content_detail.html', {
        'content': content,
        'next_url': next_url,
        'form': form,
        'user_interaction': user_interaction,
        'liked': liked,
        'disliked': disliked,
        'content_url': content_url,
    })


def get_plantilla_blocks(request, plantilla_id):
    """
    Obtiene los bloques asociados a una plantilla específica.
    
    Devuelve un JSON con los detalles de los bloques, como tipo, texto, posición y tamaño.
    """
    plantilla = get_object_or_404(Plantilla, id=plantilla_id)
    
    blocks = [{
        'id': bloque.id,
        'type': bloque.tipo,
        'content_text': bloque.contenido,
        'multimedia': bloque.multimedia.url if bloque.multimedia else None,
        'top': bloque.posicion_top,
        'left': bloque.posicion_left,
        'width': bloque.width,
        'height': bloque.height
    } for bloque in plantilla.bloques.all()]

    return JsonResponse({'blocks': blocks})


def agregar_comentario(request, pk):
    """
    Agrega un comentario a un contenido específico.
    
    Verifica si el formulario de comentario es válido y lo guarda en la base de datos.
    """
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
    if request.user.is_superuser:
        contents = Content.objects.all().order_by('created_at')
        categorias = Categorias.objects.all()
    else:
        permisos_requeridos = [
            'Contenido: Inactivar',
            'Contenido: Publicar',
            'Contenido: Eliminar',
            'Contenido: Ver historial'
        ]
        roles_con_permisos = Rol.objects.filter(permisos__nombre__in=permisos_requeridos).values_list('id', flat=True)
        categorias_permitidas = RolEnCategoria.objects.filter(usuario_id=request.user.id, rol_id__in=roles_con_permisos).values_list('categoria_id', flat=True)
        contents = Content.objects.filter(categoria_id__in=categorias_permitidas).order_by('created_at')
        categorias = Categorias.objects.filter(id__in=categorias_permitidas)
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
            content.published_started_at = timezone.now()  # Guardar la fecha y hora actual de publicación
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



def cambiar_estado_contenido(request, pk, nuevo_estado):
    """
    Cambia el estado de un contenido a 'review', 'published', 'rejected' o 'inactive'.
    

    Luego notifica por correo al autor del contenido
    """
    content = get_object_or_404(Content, pk=pk)

    # Verificar si el nuevo estado es "review" para registrar la fecha de inicio de la revisión
    if nuevo_estado == 'review':
        # Si el contenido vuelve a revisión, solo establecer la fecha de inicio si es None
        if content.revision_started_at is None:
            content.revision_started_at = timezone.now()
        # Limpiar la fecha de fin de la revisión cuando entra en revisión
        content.revision_ended_at = None
    elif (content.status == 'review' or content.status == 'inactive') and nuevo_estado == 'published':
        content.revision_ended_at = timezone.now()
        content.published_started_at = timezone.now()
    elif content.status == 'review' and nuevo_estado == 'rejected':
        # Si el contenido estaba en "review" y cambia a "published" o "rejected", registrar el fin de la revisión
        content.revision_ended_at = timezone.now()
    elif nuevo_estado == 'inactive':
        # Registrar la fecha de inactivación si el nuevo estado es "inactivo"
        content.inactivated_at = timezone.now()

    # Cambiar el estado del contenido
    content.status = nuevo_estado
    content.save()

    # Enviar correo al autor notificando el cambio de estado
    send_mail(
        subject=f'Actualización de estado para "{content.title}"',
        message=f'Hola {content.autor.username},\n\nTu contenido "{content.title}" ha cambiado de estado a "{content.status}".',
        from_email='tu_correo@gmail.com',
        recipient_list=[content.autor.email],
        fail_silently=False,
    )

    messages.success(request, f'El estado del contenido ha sido cambiado a {content.status}.')
    return redirect('content_list')

@require_POST
@login_required
def share_content(request, content_id):
    content = get_object_or_404(Content, pk=content_id)
    content.shared_count += 1
    content.save()
    return JsonResponse({'shared_count': content.shared_count})

@require_POST
@login_required
def like_content(request, pk):
    """
    Maneja la lógica de 'like' en un contenido.
    
    Si el usuario ya ha dado 'like', lo elimina; si no, lo agrega. 
    Si el usuario había dado 'dislike', también se elimina.
    """
    content = get_object_or_404(Content, pk=pk)
    interaction, created = UserInteraction.objects.get_or_create(user=request.user, content=content)

    if interaction.liked:
        interaction.liked = False
        content.likes -= 1
    else:
        interaction.liked = True
        content.likes += 1

        if interaction.disliked:
            interaction.disliked = False
            content.dislikes -= 1

    interaction.save()
    content.save()

    return JsonResponse({'likes': content.likes, 'dislikes': content.dislikes})


@require_POST
@login_required
def dislike_content(request, pk):
    """
    Maneja la lógica de 'dislike' en un contenido.
    
    Si el usuario ya ha dado 'dislike', lo elimina; si no, lo agrega.
    Si el usuario había dado 'like', también se elimina.
    """
    content = get_object_or_404(Content, pk=pk)
    interaction, created = UserInteraction.objects.get_or_create(user=request.user, content=content)

    if interaction.disliked:
        interaction.disliked = False
        content.dislikes -= 1
    else:
        interaction.disliked = True
        content.dislikes += 1

        if interaction.liked:
            interaction.liked = False
            content.likes -= 1

    interaction.save()
    content.save()

    return JsonResponse({'likes': content.likes, 'dislikes': content.dislikes})
