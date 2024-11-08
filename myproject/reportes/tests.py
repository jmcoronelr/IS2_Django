from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from content.models import Content
from Plantillas.models import Plantilla
from Categorias.models import Categorias
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class ReportesViewsTests(TestCase):
    def setUp(self):
        # Configura el cliente para realizar solicitudes
        self.client = Client()

        # Crear instancias de User, Categorias, y Plantilla necesarias para Content
        self.user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com',  # Añadir el email
            password='12345'
        )
        self.categoria = Categorias.objects.create(
            descripcionCorta="Cat Test", 
            descripcionLarga="Categoria de prueba",
            estado=True
        )
        self.plantilla = Plantilla.objects.create(
            descripcion="Plantilla de prueba",
            estado=True
        )

        # Crear algunas instancias de Content para probar
        self.content1 = Content.objects.create(
            title="Primer contenido",
            description="Descripción de prueba",
            categoria=self.categoria,
            autor=self.user,
            status="published",
            plantilla=self.plantilla,
            likes=10,
            revision_started_at=timezone.now() - timedelta(days=1),
            revision_ended_at=timezone.now(),
            published_started_at=timezone.now() - timedelta(days=2)
        )
        self.content2 = Content.objects.create(
            title="Segundo contenido",
            description="Otra descripción",
            categoria=self.categoria,
            autor=self.user,
            status="draft",
            plantilla=self.plantilla,
            likes=20,
            revision_started_at=timezone.now() - timedelta(hours=3),
            revision_ended_at=timezone.now() - timedelta(hours=2),
            published_started_at=None
        )
        self.content3 = Content.objects.create(
            title="Tercer contenido",
            description="Más detalles de prueba",
            categoria=self.categoria,
            autor=self.user,
            status="published",
            plantilla=self.plantilla,
            likes=15,
            revision_started_at=None,
            revision_ended_at=None,
            published_started_at=timezone.now() - timedelta(days=3)
        )

    def test_reportes_home(self):
        # Prueba para la vista reportes_home
        response = self.client.get(reverse('reportes_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reportes/reportes_home.html')

    def test_reporte_likes_json(self):
        # Prueba para la vista reporte_likes_json
        response = self.client.get(reverse('reporte_likes_json'))
        self.assertEqual(response.status_code, 200)
        
        # Convertir la respuesta en formato JSON y validar su contenido
        data = response.json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['title'], "Segundo contenido")  # Contenido con más likes
        self.assertEqual(data[0]['likes'], 20)

    def test_reporte_revision_json(self):
        # Prueba para la vista reporte_revision_json
        response = self.client.get(reverse('reporte_revision_json'))
        self.assertEqual(response.status_code, 200)
        
        # Convertir la respuesta en formato JSON y validar su contenido
        data = response.json()
        self.assertEqual(len(data), 2)  # Solo content1 y content2 tienen tiempos de revisión
        
        # Validar el formato del tiempo de revisión
        self.assertIn('tiempo_revision', data[0])
        self.assertIn('status', data[0])

    def test_reporte_titulos_publicados_json(self):
        # Prueba para la vista reporte_titulos_publicados_json
        response = self.client.get(reverse('reporte_publicados_json'))
        self.assertEqual(response.status_code, 200)
        
        # Convertir la respuesta en formato JSON y validar su contenido
        data = response.json()
        self.assertEqual(len(data), 2)  # Solo content1 y content3 están publicados
        self.assertEqual(data[0]['title'], "Primer contenido")
        self.assertIsNotNone(data[0]['published_started_at'])