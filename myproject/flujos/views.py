from django.shortcuts import render
from content.models import Content
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from content.models import Content
import json
from django.utils import timezone
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

        # Verificar si el nuevo estado es "review" para registrar la fecha de inicio de la revisión
        if new_status == 'review':
            # Si el contenido vuelve a revisión, solo establecer la fecha de inicio si es None
            if content.revision_started_at is None:
                content.revision_started_at = timezone.now()
            # Limpiar la fecha de fin de la revisión cuando entra en revisión
            content.revision_ended_at = None
        elif content.status == 'review' and new_status in ['published', 'rejected']:
            # Si el contenido estaba en "review" y cambia a "published" o "rejected", registrar el fin de la revisión
            content.revision_ended_at = timezone.now()

        # Cambiar el estado del contenido
        content.status = new_status
        content.save()

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'error'}, status=400)