import os
from datetime import datetime
from django.test import TestCase, Client
from django.urls import reverse
from .models import Plantilla

# Registro de pruebas unitarias
def log_unittest(artifact_name, test_name, result):
    log_dir = os.path.join(os.getcwd(), "unittest_logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, "unittest_log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - Tested: {artifact_name}.{test_name} - Result: {result}\n")


class PlantillaViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.plantilla = Plantilla.objects.create(
            descripcion="Plantilla Test",
            estado=True
        )

    def test_plantilla_list_view(self):
        """Test the list view for plantillas"""
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
        """Test the create view for plantillas"""
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
        """Test the edit view for plantillas"""
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
        """Test the delete view for plantillas"""
        try:
            response = self.client.post(reverse('plantilla_delete', args=[self.plantilla.pk]))
            self.assertEqual(response.status_code, 302)  # Redirección después de eliminar
            self.assertFalse(Plantilla.objects.filter(pk=self.plantilla.pk).exists())
            log_unittest('PlantillaDeleteView', 'test_plantilla_delete_view', 'PASSED')
        except AssertionError as e:
            log_unittest('PlantillaDeleteView', 'test_plantilla_delete_view', 'FAILED')
            raise e
