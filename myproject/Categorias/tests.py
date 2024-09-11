import os
from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse
from .models import Categorias

def log_unittest(artifact_name, test_name, result):
    """
    Registra los resultados de las pruebas unitarias en un archivo de texto.

    Parámetros:
    - artifact_name (str): El nombre del artefacto (vista o modelo) que se está probando.
    - test_name (str): El nombre de la prueba que se ejecuta.
    - result (str): El resultado de la prueba, que puede ser 'PASSED' o 'FAILED'.

    El log se guarda en un archivo llamado 'unittest_log.txt', dentro de una carpeta
    'unittest_logs' en el directorio actual del proyecto.
    """
    log_dir = os.path.join(os.getcwd(), "unittest_logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, "unittest_log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - Tested: {artifact_name}.{test_name} - Result: {result}\n")


class CategoriaViewTestCase(TestCase):
    """
    Clase que contiene las pruebas unitarias para las vistas relacionadas con el modelo `Categorias`.
    Utiliza el cliente de pruebas de Django para realizar solicitudes HTTP a las vistas y verificar
    que las respuestas sean correctas.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas. Se ejecuta antes de cada prueba.
        Crea una instancia de `Categorias` que se utilizará en las pruebas.
        """
        self.client = Client()
        self.categoria = Categorias.objects.create(
            descripcionCorta="Categoria Test",
            descripcionLarga="Descripción de prueba",
            estado=True
        )

    def test_categoria_list_view(self):
        """
        Prueba la vista de listado de categorías.

        Se asegura de que la vista devuelva un código de estado 200, que utilice
        la plantilla correcta ('Categorias/categoria_list.html') y que el contenido
        de la respuesta incluya la categoría de prueba.
        """
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
        """
        Prueba la vista de creación de categorías.

        Envía una solicitud POST a la vista para crear una nueva categoría y
        verifica que la respuesta sea una redirección (código de estado 302).
        """
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
        """
        Prueba la vista de edición de categorías.

        Envía una solicitud POST para modificar una categoría existente, verifica que la respuesta
        sea una redirección y que los cambios se guarden correctamente en la base de datos.
        """
        try:
            response = self.client.post(reverse('categoria_edit', args=[self.categoria.pk]), {
                'descripcionCorta': 'Categoria Edit',
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
        """
        Prueba la vista de eliminación de categorías.

        Envía una solicitud POST para eliminar una categoría existente, verifica que la
        respuesta sea una redirección y que la categoría haya sido eliminada de la base de datos.
        """
        try:
            response = self.client.post(reverse('categoria_delete', args=[self.categoria.pk]))
            self.assertEqual(response.status_code, 302)  # Redirección después de eliminar
            self.assertFalse(Categorias.objects.filter(pk=self.categoria.pk).exists())
            log_unittest('CategoriaDeleteView', 'test_categoria_delete_view', 'PASSED')
        except AssertionError as e:
            log_unittest('CategoriaDeleteView', 'test_categoria_delete_view', 'FAILED')
            raise e