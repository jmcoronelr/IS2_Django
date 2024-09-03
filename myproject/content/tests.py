from django.test import TestCase
from django.urls import reverse
from .models import Content, Category

class ContentDeleteViewTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Test Category', description='Test Description')
        self.content = Content.objects.create(
            title='Test Content',
            description='Test Content Description',
            category=self.category,
            status='draft'
        )

    def test_delete_content(self):
        # Obtiene la URL para eliminar el contenido
        delete_url = reverse('content_delete', args=[self.content.pk]) + '?page=2'
        response = self.client.post(delete_url)

        # Verifica que el contenido ha sido eliminado
        self.assertEqual(Content.objects.count(), 0)

        # Verifica que el usuario ha sido redirigido a la página 2 de la lista
        self.assertRedirects(response, '/content/?page=2')
class ContentListViewTest(TestCase):

    def setUp(self):
        self.category1 = Category.objects.create(name='Category 1', description='Description 1')
        self.category2 = Category.objects.create(name='Category 2', description='Description 2')
        Content.objects.create(title='Content 1', description='Desc 1', category=self.category1, status='draft')
        Content.objects.create(title='Content 2', description='Desc 2', category=self.category1, status='review')
        Content.objects.create(title='Content 3', description='Desc 3', category=self.category2, status='published')

    def test_filter_by_status(self):
        response = self.client.get('/content/', {'estado': 'draft'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Content 1')
        self.assertNotContains(response, 'Content 2')
        self.assertNotContains(response, 'Content 3')

    def test_filter_by_category(self):
        response = self.client.get('/content/', {'categoria': self.category1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Content 1')
        self.assertContains(response, 'Content 2')
        self.assertNotContains(response, 'Content 3')
class ContentPaginationTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Category 1', description='Description 1')
        for i in range(15):
            Content.objects.create(title=f'Content {i}', description=f'Description {i}', category=self.category, status='draft')

    def test_pagination_is_correct(self):
        response = self.client.get('/content/')
        self.assertEqual(response.status_code, 200)
        # Verifica que haya un máximo de 10 elementos en la primera página
        self.assertEqual(len(response.context['contents']), 10)

        # Verifica que la segunda página tenga los elementos restantes
        response = self.client.get('/content/', {'page': 2})
        self.assertEqual(len(response.context['contents']), 5)
