from django.shortcuts import render
from content.models import Content
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from content.models import Content
import json
from django.core.mail import send_mail

def flujos_home(request):
    # Obtenemos los contenidos por estado
    borradores = Content.objects.filter(status='draft')
    en_revision = Content.objects.filter(status='review')
    publicados = Content.objects.filter(status='published')
    rechazados = Content.objects.filter(status='rejected')

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