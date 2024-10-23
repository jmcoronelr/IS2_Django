from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Content
from .forms import ContentForm, ComentarioForm
import datetime
from Plantillas.models import Plantilla  # Importa el modelo Plantilla
from django.http import JsonResponse
import json
from .models import Content, ContentBlock
from Categorias.models import Categorias
from roles.models import RolEnCategoria, Rol
from historial.models import Historial
from django.contrib import messages
from content.models import UserInteraction
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
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
            'Contenido: Editar propio', 'Contenido: Inactivar', 'Contenido: Publicar',
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
        contents= contents.filter(author=request.user)
    else:
        contents = contents.exclude(author=request.user)

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


from django.core.mail import send_mail

def content_create_edit(request, pk=None):
    """
    Crea o edita un contenido.

    Si se proporciona una clave primaria (pk), se edita el contenido existente; de lo contrario, se crea uno nuevo.
    Solo los superusuarios pueden ver todas las categorías; los demás usuarios ven categorías según sus roles.
    Maneja la carga de bloques de contenido dinámicos y actualiza el historial de cambios del contenido.

    Cuando se aprieta el boton editar entra a revision y ahi se guarda para el tema de los reportes
    """
    if pk:
        content = get_object_or_404(Content, pk=pk)
        accion = 'editado'
        old_status = content.status  # Guarda el estado anterior
        content.status = 'review'
        # Verificar si revision_started_at está vacío y el contenido pasa a revisión
        if content.revision_started_at is None:
            content.revision_started_at = timezone.now()        
    else:
        content = None
        accion = 'creado'
        old_status = None  # No hay estado anterior si es nuevo

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
            content.author = request.user

            # Asigna el autor solo si es un contenido nuevo
            if not pk:
                content.autor = request.user

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

            new_status = content.status  # Guarda el nuevo estado

            content.save()

            # Enviar correo solo si el estado ha cambiado
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
        'categorias': categorias,
        'selected_plantilla': selected_plantilla,
        'selected_categoria': selected_categoria,
        'blocks': blocks,
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
            return redirect('content_detail', pk=content.pk)
    else:
        form = ComentarioForm()

    return render(request, 'content/content_detail.html', {
        'content': content,
        'next_url': next_url,
        'form': form,
        'user_interaction': user_interaction,
        'liked': liked,
        'disliked': disliked,
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




def cambiar_estado_contenido(request, pk, nuevo_estado):
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