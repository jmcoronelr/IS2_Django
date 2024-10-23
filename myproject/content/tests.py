from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from content.models import Content, Comentario
from Categorias.models import Categorias
from django.db import IntegrityError

#TEST CASES PARA LA GESTIÓN DE CONTENIDOS

#Este test verificará que se puede crear contenido correctamente.
class ContentCreateViewTest(TestCase):

    def setUp(self):
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
            status='draft'
        )
        self.assertEqual(Content.objects.count(), 1)
        self.assertEqual(content.title, 'New Content')


#Este test verificará que se puede modificar contenido
class ContentUpdateViewTest(TestCase):

    def setUp(self):
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True 
        )
        self.content = Content.objects.create(
            title='Old Content',
            description='Old Description',
            categoria=self.category,
            status='draft'
        )

    def test_update_content(self):
        self.content.title = 'Updated Content'
        self.content.description = 'Updated Description'
        self.content.save()
        updated_content = Content.objects.get(pk=self.content.pk)
        self.assertEqual(updated_content.title, 'Updated Content')
        self.assertEqual(updated_content.description, 'Updated Description')


#Este test verificará que se puede eliminar un contenido.
class ContentDeleteViewTest(TestCase):

    def setUp(self):
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True  
        )
        self.content = Content.objects.create(
            title='Test Content',
            description='Test Content Description',
            categoria=self.category,
            status='draft'
        )

    def test_delete_content(self):
        self.content.delete()
        self.assertEqual(Content.objects.count(), 0)

#TEST CASES PARA LA GESTIÓN DE ESTADOS DEL CONTENIDO

#Este test verificará que se puede cambiar el estado de un contenido.
class ContentStatusTest(TestCase):

    def setUp(self):
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True  
        )
        self.content = Content.objects.create(
            title='Status Test Content',
            description='Testing Status Change',
            categoria=self.category,
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

#Test Cases para la asignación de categoría
# Este test verificará que no se puede asignar un contenido sin categoría
class ContentCategoryAssignmentTest(TestCase):
    
    def setUp(self):
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
                status='draft'
            )

#Test case para la búsqueda y filtrado
class ContentFilteringTest(TestCase):

    def setUp(self):
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True
        )
        self.content1 = Content.objects.create(
            title='Alpha Content',
            description='Content A',
            categoria=self.category,
            status='draft'
        )
        self.content2 = Content.objects.create(
            title='Beta Content',
            description='Content B',
            categoria=self.category,
            status='published'
        )

    def test_filter_by_title(self):
        contents = Content.objects.filter(title__icontains='Alpha')
        self.assertEqual(contents.count(), 1)

    def test_filter_by_status(self):
        contents = Content.objects.filter(status='published')
        self.assertEqual(contents.count(), 1)


#Test case para comentarios 
User = get_user_model()

class ContentCommentTest(TestCase):

    def setUp(self):
        # Crear una categoría y un usuario de prueba
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True
        )
        
        # Crear contenido de prueba
        self.content = Content.objects.create(
            title='Content with Comments',
            description='Content Description',
            categoria=self.category,
            status='published'
        )

        # Crear un autor de comentario (usuario)
        self.author = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
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
        self.assertEqual(comment.autor.username, 'testuser')

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

#Test case para listar contenidos
#Este test verificará que un usuario puede ver la lista de contenidos filtrados correctamente según permisos
class ContentListViewTest(TestCase):

    def setUp(self):
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True
        )
        self.content1 = Content.objects.create(
            title='Content One',
            description='Content Description 1',
            categoria=self.category,
            status='published'
        )
        self.content2 = Content.objects.create(
            title='Content Two',
            description='Content Description 2',
            categoria=self.category,
            status='draft'
        )

    def test_content_list_view_as_superuser(self):
        # Crear un usuario superusuario
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client.login(username='admin', password='password123')
        
        # Llamar a la vista content_list
        response = self.client.get(reverse('content_list'))

        # Verificar que todos los contenidos están presentes
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Content One')
        self.assertContains(response, 'Content Two')

    def test_content_list_view_as_non_superuser(self):
        # Crear un usuario normal
        user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='password123'
        )
        self.client.login(username='user', password='password123')
        
        # Llamar a la vista content_list
        response = self.client.get(reverse('content_list'))

        # Verificar que el estado es 200 pero no contiene contenidos si no tiene permisos
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Content One')
        self.assertNotContains(response, 'Content Two')


#Test de paginación de contenidos

class ContentPaginationTest(TestCase):

    def setUp(self):
        # Crear una categoría
        self.category = Categorias.objects.create(
            descripcionCorta='Test Category',
            descripcionLarga='Test Description',
            estado=True
        )
        
        # Crear 15 contenidos para probar la paginación
        for i in range(15):
            Content.objects.create(
                title=f'Content {i + 1}',
                description=f'Content Description {i + 1}',
                categoria=self.category,
                status='published'
            )

    def test_content_pagination(self):
        # Iniciar sesión como superusuario para ver todos los contenidos
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password123'
        )
        self.client.login(username='admin', password='password123')

        # Llamar a la vista content_list para la primera página
        response = self.client.get(reverse('content_list') + '?page=1')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la primera página contiene exactamente 8 contenidos
        self.assertEqual(len(response.context['contents']), 8)
        self.assertContains(response, 'Content 1')
        self.assertContains(response, 'Content 8')

        # Llamar a la vista content_list para la segunda página
        response = self.client.get(reverse('content_list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la segunda página contiene los restantes 7 contenidos
        self.assertEqual(len(response.context['contents']), 7)
        self.assertContains(response, 'Content 9')
        self.assertContains(response, 'Content 15')