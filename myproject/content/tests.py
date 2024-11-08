from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from content.models import Content, Comentario
from Categorias.models import Categorias
from django.db import IntegrityError

User = get_user_model()

# TEST CASES PARA LA GESTIÓN DE CONTENIDOS

# Este test verificará que se puede crear contenido correctamente.
class ContentCreateViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True  
        )

    def test_create_content(self):
        content = Content.objects.create(
            title='New Content',
            description='New Content Description',
            categoria=self.category,
            autor=self.user,
            status='draft'
        )
        self.assertEqual(Content.objects.count(), 1)
        self.assertEqual(content.title, 'New Content')
        self.assertEqual(content.autor, self.user)


# Este test verificará que se puede modificar contenido
class ContentUpdateViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True 
        )
        self.content = Content.objects.create(
            title='Old Content',
            description='Old Description',
            categoria=self.category,
            autor=self.user,
            status='draft'
        )

    def test_update_content(self):
        self.content.title = 'Updated Content'
        self.content.description = 'Updated Description'
        self.content.save()
        updated_content = Content.objects.get(pk=self.content.pk)
        self.assertEqual(updated_content.title, 'Updated Content')
        self.assertEqual(updated_content.description, 'Updated Description')


# Este test verificará que se puede eliminar un contenido.
class ContentDeleteViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True  
        )
        self.content = Content.objects.create(
            title='Test Content',
            description='Test Content Description',
            categoria=self.category,
            autor=self.user,
            status='draft'
        )

    def test_delete_content(self):
        self.content.delete()
        self.assertEqual(Content.objects.count(), 0)

# TEST CASES PARA LA GESTIÓN DE ESTADOS DEL CONTENIDO

# Este test verificará que se puede cambiar el estado de un contenido.
class ContentStatusTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True  
        )
        self.content = Content.objects.create(
            title='Status Test Content',
            description='Testing Status Change',
            categoria=self.category,
            autor=self.user,
            status='draft'
        )

    def test_change_content_status(self):
        self.content.status = 'published'
        self.content.save()
        self.assertEqual(self.content.status, 'published')

        self.content.status = 'review'
        self.content.save()
        self.assertEqual(self.content.status, 'review')

        self.content.status = 'rejected'
        self.content.save()
        self.assertEqual(self.content.status, 'rejected')

        self.content.status = 'draft'
        self.content.save()
        self.assertEqual(self.content.status, 'draft')

        self.content.status = 'inactive'
        self.content.save()
        self.assertEqual(self.content.status, 'inactive')

# Test Cases para la asignación de categoría
# Este test verificará que no se puede asignar un contenido sin categoría
class ContentCategoryAssignmentTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True
        )

    def test_category_assignment(self):
        content = Content.objects.create(
            title='Content with Category',
            description='Content Description',
            categoria=self.category,
            autor=self.user,
            status='draft'
        )
        self.assertEqual(content.categoria.descripcionCorta, 'Test Category')

    def test_invalid_category_assignment(self):
        # Verificamos que la excepción lanzada sea IntegrityError
        with self.assertRaises(IntegrityError):
            Content.objects.create(
                title='Content with Invalid Category',
                description='Content Description',
                categoria=None,  # No asignar una categoría
                autor=self.user,
                status='draft'
            )

# Test case para la búsqueda y filtrado
class ContentFilteringTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True
        )
        self.content1 = Content.objects.create(
            title='Alpha Content',
            description='Content A',
            categoria=self.category,
            autor=self.user,
            status='draft'
        )
        self.content2 = Content.objects.create(
            title='Beta Content',
            description='Content B',
            categoria=self.category,
            autor=self.user,
            status='published'
        )

    def test_filter_by_title(self):
        contents = Content.objects.filter(title__icontains='Alpha')
        self.assertEqual(contents.count(), 1)

    def test_filter_by_status(self):
        contents = Content.objects.filter(status='published')
        self.assertEqual(contents.count(), 1)


# Test case para comentarios 
class ContentCommentTest(TestCase):

    def setUp(self):
        # Crear una categoría y un usuario de prueba
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True
        )
        
        # Crear contenido de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.content = Content.objects.create(
            title='Content with Comments',
            description='Content Description',
            categoria=self.category,
            autor=self.user,
            status='published'
        )

        # Crear un autor de comentario (usuario)
        self.author = User.objects.create_user(
            username='commentuser',
            email='commentuser@example.com',
            password='password123'
        )

    def test_add_comment(self):
        # Crear un comentario asociado al contenido
        comment = Comentario.objects.create(
            contenido=self.content,
            autor=self.author,
            texto='This is a test comment'
        )
        
        # Verificar que el comentario se haya agregado correctamente
        self.assertEqual(self.content.comentarios.count(), 1)
        self.assertEqual(comment.texto, 'This is a test comment')
        self.assertEqual(comment.autor.username, 'commentuser')

    def test_delete_comment(self):
        # Crear un comentario
        comment = Comentario.objects.create(
            contenido=self.content,
            autor=self.author,
            texto='This is a test comment'
        )
        
        # Eliminar el comentario
        comment.delete()
        
        # Verificar que el comentario se haya eliminado
        self.assertEqual(self.content.comentarios.count(), 0)

from unittest.mock import MagicMock
from django.test import RequestFactory
from django.core import mail
from django.contrib.auth import get_user_model
from content.views import cambiar_estado_contenido

User = get_user_model()

class ContentStatusEmailNotificationTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True
        )
        self.content = Content.objects.create(
            title='Content for Email Test',
            description='Testing email notification on status change',
            categoria=self.category,
            autor=self.user,
            status='draft'
        )
        self.factory = RequestFactory()

    def test_email_sent_on_status_change(self):
        # Crear una solicitud simulada
        request = self.factory.get(reverse('content_list'))
        request.user = self.user

        # Mock del sistema de mensajes
        request._messages = MagicMock()

        # Cambiar el estado del contenido a 'review'
        cambiar_estado_contenido(request, pk=self.content.pk, nuevo_estado='review')

        # Verificar que se envió un correo electrónico
        self.assertEqual(len(mail.outbox), 1)
        
        # Verificar el contenido del correo
        email = mail.outbox[0]
        self.assertEqual(email.subject, f'Actualización de estado para "{self.content.title}"')
        self.assertIn(f'Hola {self.user.username}', email.body)
        self.assertIn(f'Tu contenido "{self.content.title}" ha cambiado de estado a "review".', email.body)
        self.assertEqual(email.to, [self.user.email])
