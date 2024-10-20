from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Content, Historial
from Categorias.models import Categorias
from usuarios.models import Usuario

class HistorialContentViewTests(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = Usuario.objects.create_user(username='testuser',email='testuser@mail.com', password='12345')
        
        # Crear una categoría de prueba
        self.categoria = Categorias.objects.create(
            descripcionCorta="Tech",
            descripcionLarga="Categoría de tecnología",
            estado=True
        )
        
        # Crear una plantilla de prueba
        
        # Crear un contenido de prueba
        self.content = Content.objects.create(
            title="Test Content",
            description="This is a test content",
            categoria=self.categoria,
            status='draft',
        )
        
        # Crear varias versiones del historial para el contenido
        self.historial_1 = Historial.objects.create(
            content=self.content,
            user=self.user,
            version=1,
            cambio="Primera versión del contenido",
            timestamp=timezone.now()
        )
        
        self.historial_2 = Historial.objects.create(
            content=self.content,
            user=self.user,
            version=2,
            cambio="Segunda versión del contenido",
            timestamp=timezone.now()
        )
        
        self.historial_3 = Historial.objects.create(
            content=self.content,
            user=self.user,
            version=3,
            cambio="Tercera versión del contenido",
            timestamp=timezone.now()
        )
        
    def test_historial_content_view_success(self):
        # Test que verifica el acceso exitoso a la vista con un contenido existente
        url = reverse('historial_content', args=[self.content.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'historial/historial_content.html')
        self.assertEqual(response.context['content'], self.content)
        
        # Verificar que el historial está ordenado por versión descendente
        historial = response.context['historial']
        self.assertEqual(list(historial), [self.historial_3, self.historial_2, self.historial_1])

    def test_historial_content_view_404(self):
        # Test que verifica que se devuelve un 404 cuando el contenido no existe
        url = reverse('historial_content', args=[999])  # Un pk que no existe
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_historial_order_by_version_desc(self):
        # Test que verifica específicamente que los objetos Historial están ordenados por versión descendente
        url = reverse('historial_content', args=[self.content.pk])
        response = self.client.get(url)
        
        historial = response.context['historial']
        versions = [h.version for h in historial]
        self.assertEqual(versions, [3, 2, 1])  # Verificar que las versiones están en orden descendente

    def test_historial_content_view_shows_correct_user(self):
        # Test para verificar que se muestra el usuario correcto en cada entrada de historial
        url = reverse('historial_content', args=[self.content.pk])
        response = self.client.get(url)
        
        historial = response.context['historial']
        for h in historial:
            self.assertEqual(h.user, self.user)  # Verificar que el usuario es el correcto en todas las versiones
