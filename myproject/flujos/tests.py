from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from content.models import Content, Categorias
from usuarios.models import Usuario  # Importar el modelo personalizado
import json

class FlujoContentTestCase(TestCase):
    
    def setUp(self):
        # Crear una categoría y contenido en estado 'borrador'
        self.categoria = Categorias.objects.create(
            descripcionCorta="Tech", 
            descripcionLarga="Tecnología", 
            estado=True
        )
        self.content = Content.objects.create(
            title="Nuevo Contenido", 
            description="Descripción de prueba", 
            categoria=self.categoria, 
            status="draft"
        )
        # Utilizar el modelo de usuario personalizado 'Usuario' y proporcionar el campo 'email'
        self.user = Usuario.objects.create_user(
            username='testuser', 
            password='12345', 
            email='testuser@example.com'  # Añadir el email
        )

    def test_crear_content(self):
        """
        Prueba para verificar la creación de contenido.
        Valida que el contenido ha sido creado correctamente con el título y descripción adecuados.
        """
        content = Content.objects.get(title="Nuevo Contenido")
        self.assertEqual(content.status, 'draft')
        self.assertEqual(content.description, 'Descripción de prueba')

    def test_update_content_status_to_revision(self):
        """
        Prueba para actualizar el estado de un contenido a 'review'.
        Verifica que el estado se actualice correctamente y que el proceso
        de revisión haya sido iniciado (fecha de inicio de revisión registrada).
        """
        response = self.client.post(reverse('update_content_status'), json.dumps({
            'content_id': self.content.id,
            'new_status': 'review'
        }), content_type="application/json")
        self.content.refresh_from_db()
        self.assertEqual(self.content.status, 'review')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(self.content.revision_started_at)
    
    def test_update_content_status_to_published(self):
        """
        Prueba para actualizar el estado del contenido a 'published'.
        Simula que el contenido ya está en estado de revisión antes de ser publicado.
        Verifica que el contenido se publique correctamente y que se registre
        la fecha de finalización de la revisión.
        """
        self.content.status = 'review'
        self.content.revision_started_at = timezone.now()
        self.content.save()
        
        response = self.client.post(reverse('update_content_status'), json.dumps({
            'content_id': self.content.id,
            'new_status': 'published'
        }), content_type="application/json")
        self.content.refresh_from_db()
        self.assertEqual(self.content.status, 'published')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(self.content.revision_ended_at)

    def test_update_content_status_to_rejected(self):
        """
        Prueba para actualizar el estado del contenido a 'rejected'.
        Simula que el contenido ya está en estado de revisión antes de ser rechazado.
        Verifica que el estado se actualice correctamente y que se registre la fecha
        de finalización de la revisión.
        """
        self.content.status = 'review'
        self.content.revision_started_at = timezone.now()
        self.content.save()
        
        response = self.client.post(reverse('update_content_status'), json.dumps({
            'content_id': self.content.id,
            'new_status': 'rejected'
        }), content_type="application/json")
        self.content.refresh_from_db()
        self.assertEqual(self.content.status, 'rejected')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(self.content.revision_ended_at)

    def test_update_content_status_to_inactive(self):
        """
        Prueba para cambiar el estado del contenido a 'inactive'.
        Verifica que el estado se actualice correctamente y que no afecte
        las fechas de revisión (no deben estar presentes).
        """

        response = self.client.post(reverse('update_content_status'), json.dumps({
            'content_id': self.content.id,
            'new_status': 'inactive'
        }), content_type="application/json")
        self.content.refresh_from_db()
        self.assertEqual(self.content.status, 'inactive')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.content.revision_started_at)  # No debe haber iniciado revisión
        self.assertIsNone(self.content.revision_ended_at)    # No debe haber finalizado revisión

    def test_update_content_status_to_same_state(self):
        """
        Prueba para intentar cambiar el estado del contenido a su estado actual.
        Verifica que no se realicen cambios en el estado del contenido y que la solicitud
        se maneje correctamente devolviendo un código de estado 200.
        """
        response = self.client.post(reverse('update_content_status'), json.dumps({
            'content_id': self.content.id,
            'new_status': 'draft'  # Estado ya existente
        }), content_type="application/json")
        self.content.refresh_from_db()
        self.assertEqual(self.content.status, 'draft')  # El estado no debe cambiar
        self.assertEqual(response.status_code, 200)
