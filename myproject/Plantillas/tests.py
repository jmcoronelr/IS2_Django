import os
from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse
from .models import Plantilla

# Registro de pruebas unitarias
def log_unittest(artifact_name, test_name, result):
    """
    Registra los resultados de las pruebas unitarias en un archivo de texto.

    Parámetros:
    - artifact_name (str): El nombre del artefacto (como una vista o modelo) que se está probando.
    - test_name (str): El nombre de la prueba que se ejecuta.
    - result (str): El resultado de la prueba, que puede ser 'PASSED' o 'FAILED'.

    La función guarda los registros en un archivo 'unittest_log.txt' dentro de una carpeta
    'unittest_logs' en el directorio actual del proyecto.
    """
    log_dir = os.path.join(os.getcwd(), "unittest_logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, "unittest_log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - Tested: {artifact_name}.{test_name} - Result: {result}\n")


class PlantillaViewTestCase(TestCase):
    """
    Clase que contiene las pruebas unitarias para las vistas relacionadas con el modelo `Plantilla`.
    Utiliza el cliente de pruebas de Django para realizar solicitudes HTTP a las vistas
    y verificar que las respuestas sean correctas.
    """

    def setUp(self):
        """
        Configuración inicial para las pruebas. Se ejecuta antes de cada prueba.
        Crea una instancia de `Plantilla` que se utilizará en las pruebas.
        """
        self.client = Client()
        self.plantilla = Plantilla.objects.create(
            descripcion="Plantilla Test",
            estado=True
        )

    def test_plantilla_list_view(self):
        """
        Prueba la vista de listado de plantillas.

        Verifica que la vista devuelva un código de estado 200, que utilice
        la plantilla correcta ('Plantillas/plantilla_list.html') y que el contenido
        de la respuesta incluya la plantilla de prueba.
        """
        try:
            response = self.client.get(reverse('plantilla_list'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'Plantillas/plantilla_list.html')
            self.assertContains(response, "Plantilla Test")
            log_unittest('PlantillaListView', 'test_plantilla_list_view', 'PASSED')
        except AssertionError as e:
            log_unittest('PlantillaListView', 'test_plantilla_list_view', 'FAILED')
            raise e

    def test_plantilla_create_view(self):
        """
        Prueba la vista de creación de plantillas.

        Envía una solicitud POST a la vista para crear una nueva plantilla y
        verifica que la respuesta sea una redirección (código de estado 302).
        """
        try:
            response = self.client.post(reverse('plantilla_create'), {
                'descripcion': 'Nueva Plantilla',
                'estado': True
            })
            self.assertEqual(response.status_code, 302)  # Redirección después de crear
            log_unittest('PlantillaCreateView', 'test_plantilla_create_view', 'PASSED')
        except AssertionError as e:
            log_unittest('PlantillaCreateView', 'test_plantilla_create_view', 'FAILED')
            raise e

    def test_plantilla_edit_view(self):
        """
        Prueba la vista de edición de plantillas.

        Envía una solicitud POST para modificar una plantilla existente,
        verifica que la respuesta sea una redirección y que los cambios
        se guarden correctamente en la base de datos.
        """
        try:
            response = self.client.post(reverse('plantilla_edit', args=[self.plantilla.pk]), {
                'descripcion': 'Plantilla Test Editada',
                'estado': False
            })
            self.assertEqual(response.status_code, 302)  # Redirección después de editar
            self.plantilla.refresh_from_db()
            self.assertEqual(self.plantilla.descripcion, 'Plantilla Test Editada')
            log_unittest('PlantillaEditView', 'test_plantilla_edit_view', 'PASSED')
        except AssertionError as e:
            log_unittest('PlantillaEditView', 'test_plantilla_edit_view', 'FAILED')
            raise e

    def test_plantilla_delete_view(self):
        """
        Prueba la vista de eliminación de plantillas.

        Envía una solicitud POST para eliminar una plantilla existente,
        verifica que la respuesta sea una redirección y que la plantilla
        haya sido eliminada de la base de datos.
        """
        try:
            response = self.client.post(reverse('plantilla_delete', args=[self.plantilla.pk]))
            self.assertEqual(response.status_code, 302)  # Redirección después de eliminar
            self.assertFalse(Plantilla.objects.filter(pk=self.plantilla.pk).exists())
            log_unittest('PlantillaDeleteView', 'test_plantilla_delete_view', 'PASSED')
        except AssertionError as e:
            log_unittest('PlantillaDeleteView', 'test_plantilla_delete_view', 'FAILED')
            raise e
