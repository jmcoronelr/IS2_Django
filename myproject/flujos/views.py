from django.shortcuts import render
from content.models import Content
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from content.models import Content
import json
from django.utils import timezone
from django.core.mail import send_mail
from roles.models import RolEnCategoria, Rol

def flujos_home(request):
    if request.user.is_superuser:
        contents = Content.objects.all().order_by('created_at')
    else:
        permisos_estado = [
            'Contenido: Mandar a borrador',
            'Contenido: Mandar a revisión',
            'Contenido: Publicar',
            'Contenido: Rechazar',
        ]
        roles_con_permisos = Rol.objects.filter(permisos__nombre__in=permisos_estado).values_list('id', flat=True)
        categorias_permitidas = RolEnCategoria.objects.filter(usuario_id=request.user.id, rol_id__in=roles_con_permisos).values_list('categoria_id', flat=True)
        contents = Content.objects.filter(categoria_id__in=categorias_permitidas).order_by('created_at')
    
    # Obtenemos los contenidos por estado
    borradores = contents.filter(status='draft')
    en_revision = contents.filter(status='review')
    publicados = contents.filter(status='published')
    rechazados = contents.filter(status='rejected')

    return render(request, 'flujos/flujos_home.html', {
        'borradores': borradores,
        'en_revision': en_revision,
        'publicados': publicados,
        'rechazados': rechazados,
    })


@csrf_exempt
def update_content_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        content_id = data.get('content_id')
        new_status = data.get('new_status')

        # Actualizamos el estado del contenido
        content = Content.objects.get(id=content_id)

        # Verificar si el nuevo estado es "review" para registrar la fecha de inicio de la revisión
        if new_status == 'review':
            # Si el contenido vuelve a revisión, actualizar la fecha de inicio de la revisión
            content.revision_started_at = timezone.now()  # Se sobreescribe cada vez que entra a revisión
            content.revision_ended_at = None  # Limpiar la fecha de fin de la revisión
            content.published_started_at = None  # Limpiar la fecha de publicación
        elif new_status == 'published':
            # Si el contenido se publica, registrar la fecha de fin de revisión y la fecha de publicación
            content.revision_ended_at = timezone.now()
            content.published_started_at = timezone.now()
        elif new_status == 'rejected':
            # Si el contenido se rechaza, registrar el fin de la revisión
            content.revision_ended_at = timezone.now()
            content.published_started_at = None  # Limpiar la fecha de publicación
        elif new_status == 'draft':
            # Si el contenido vuelve a borrador, limpiar las fechas de revisión y publicación
            content.revision_started_at = None
            content.revision_ended_at = None
            content.published_started_at = None

        # Cambiar el estado del contenido
        content.status = new_status
        content.save()

        # Enviar correo al autor notificando el cambio de estado
        send_mail(
            subject=f'Actualización de estado para "{content.title}"',
            message=f'Hola {content.autor.username},\n\nTu contenido "{content.title}" ha cambiado de estado a "{content.status}".',
            from_email='tu_correo@gmail.com',
            recipient_list=[content.autor.email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'error'}, status=400)
