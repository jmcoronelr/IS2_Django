import os
from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse
from .models import Categorias

# Registro de pruebas unitarias
def log_unittest(artifact_name, test_name, result):
    log_dir = os.path.join(os.getcwd(), "unittest_logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, "unittest_log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - Tested: {artifact_name}.{test_name} - Result: {result}\n")


class CategoriaViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.categoria = Categorias.objects.create(
            descripcionCorta="Categoria Test",
            descripcionLarga="Descripción de prueba",
            estado=True
        )

    def test_categoria_list_view(self):
        """Test the list view for categorias"""
        try:
            response = self.client.get(reverse('categoria_list'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'Categorias/categoria_list.html')
            self.assertContains(response, "Categoria Test")
            log_unittest('CategoriaListView', 'test_categoria_list_view', 'PASSED')
        except AssertionError as e:
            log_unittest('CategoriaListView', 'test_categoria_list_view', 'FAILED')
            raise e

    def test_categoria_create_view(self):
        """Test the create view for categorias"""
        try:
            response = self.client.post(reverse('categoria_create'), {
                'descripcionCorta': 'Nueva Categoria',
                'descripcionLarga': 'Descripción nueva',
                'estado': True
            })
            self.assertEqual(response.status_code, 302)  # Redirección después de crear
            log_unittest('CategoriaCreateView', 'test_categoria_create_view', 'PASSED')
        except AssertionError as e:
            log_unittest('CategoriaCreateView', 'test_categoria_create_view', 'FAILED')
            raise e

    def test_categoria_edit_view(self):
        """Test the edit view for categorias"""
        try:
            response = self.client.post(reverse('categoria_edit', args=[self.categoria.pk]), {
                'descripcionCorta': 'Categoria Edit',  # Ajustado a 15 caracteres
                'descripcionLarga': 'Descripción editada',
                'estado': False
            })
            if response.status_code != 302:
                print(response.content)  # Imprime el contenido de la respuesta si falla
            self.assertEqual(response.status_code, 302)  # Redirección después de editar
            self.categoria.refresh_from_db()
            self.assertEqual(self.categoria.descripcionCorta, 'Categoria Edit')
            log_unittest('CategoriaEditView', 'test_categoria_edit_view', 'PASSED')
        except AssertionError as e:
            log_unittest('CategoriaEditView', 'test_categoria_edit_view', 'FAILED')
            raise e



    def test_categoria_delete_view(self):
        """Test the delete view for categorias"""
        try:
            response = self.client.post(reverse('categoria_delete', args=[self.categoria.pk]))
            self.assertEqual(response.status_code, 302)  # Redirección después de eliminar
            self.assertFalse(Categorias.objects.filter(pk=self.categoria.pk).exists())
            log_unittest('CategoriaDeleteView', 'test_categoria_delete_view', 'PASSED')
        except AssertionError as e:
            log_unittest('CategoriaDeleteView', 'test_categoria_delete_view', 'FAILED')
            raise e
