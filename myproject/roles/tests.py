import os
from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from .models import Usuario, Rol, RolEnCategoria, Categorias, Permiso

def log_unittest(artifact_name, test_name, result):
    """
    Registra los resultados de las pruebas unitarias en un archivo de texto.
    
    Parámetros:
    - artifact_name (str): El nombre del artefacto (vista o modelo) que se está probando.
    - test_name (str): El nombre de la prueba que se ejecuta.
    - result (str): El resultado de la prueba, que puede ser 'PASSED' o 'FAILED'.
    """
    log_dir = os.path.join(os.getcwd(), "unittest_logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_path = os.path.join(log_dir, "unittest_log.txt")
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - Tested: {artifact_name}.{test_name} - Result: {result}\n")

class RolesViewsTestCase(TestCase):

    def setUp(self):
        """
        Configuración inicial para las pruebas.
        Crea usuarios, roles, categorías y permisos que serán utilizados en las pruebas.
        """
        self.usuario = Usuario.objects.create(username="testuser", email="test@test.com")
        self.usuario.set_password("password123")
        self.usuario.save()

        self.rol_editor = Rol.objects.create(nombre="Editor", descripcion="Puede editar contenido")
        self.categoria_tecnologia = Categorias.objects.create(
            descripcionCorta="Tecnología",
            descripcionLarga="Categoría de tecnología",
            estado=True
        )
        RolEnCategoria.objects.create(usuario=self.usuario, categoria=self.categoria_tecnologia, rol=self.rol_editor)

        self.client.login(username='testuser', password='password123')

    def test_asignar_rol_view_get(self):
        """
        Prueba la vista de asignación de roles en modo GET.
        """
        try:
            response = self.client.get(reverse('asignar_rol', kwargs={'usuario_id': self.usuario.id}))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'roles/asignar_rol.html')
            log_unittest('AsignarRolView', 'test_asignar_rol_view_get', 'PASSED')
        except AssertionError as e:
            log_unittest('AsignarRolView', 'test_asignar_rol_view_get', 'FAILED')
            raise e

    def test_asignar_rol_view_post(self):
        """
        Prueba la vista de asignación de roles en modo POST.
        """
        try:
            post_data = {
                'categoria': self.categoria_tecnologia.id,
                'rol': self.rol_editor.id
            }
            response = self.client.post(reverse('asignar_rol', kwargs={'usuario_id': self.usuario.id}), data=post_data)
            self.assertEqual(response.status_code, 302)  # Redirección
            log_unittest('AsignarRolView', 'test_asignar_rol_view_post', 'PASSED')
        except AssertionError as e:
            log_unittest('AsignarRolView', 'test_asignar_rol_view_post', 'FAILED')
            raise e

    def test_ver_usuario_view(self):
        """
        Prueba la vista para ver los roles de un usuario.
        """
        try:
            response = self.client.get(reverse('ver_usuario', kwargs={'usuario_id': self.usuario.id}))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'roles/ver_usuario.html')
            self.assertContains(response, "Editor")
            log_unittest('VerUsuarioView', 'test_ver_usuario_view', 'PASSED')
        except AssertionError as e:
            log_unittest('VerUsuarioView', 'test_ver_usuario_view', 'FAILED')
            raise e

    def test_lista_usuarios_view(self):
        """
        Prueba la vista para listar todos los usuarios.
        """
        try:
            response = self.client.get(reverse('lista_usuarios'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'roles/lista_usuarios.html')
            self.assertContains(response, self.usuario.email)
            log_unittest('ListaUsuariosView', 'test_lista_usuarios_view', 'PASSED')
        except AssertionError as e:
            log_unittest('ListaUsuariosView', 'test_lista_usuarios_view', 'FAILED')
            raise e

    def test_crear_rol_view_get(self):
        """
        Prueba la vista de creación de roles en modo GET.
        """
        try:
            response = self.client.get(reverse('crear_rol'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'roles/crear_rol.html')
            log_unittest('CrearRolView', 'test_crear_rol_view_get', 'PASSED')
        except AssertionError as e:
            log_unittest('CrearRolView', 'test_crear_rol_view_get', 'FAILED')
            raise e

    def test_crear_rol_view_post(self):
        """
        Prueba la vista de creación de roles en modo POST.
        """
        try:
            post_data = {
                'nombre': 'Moderador',
                'descripcion': 'Puede moderar comentarios'
            }
            response = self.client.post(reverse('crear_rol'), data=post_data)
            self.assertEqual(response.status_code, 302)
            log_unittest('CrearRolView', 'test_crear_rol_view_post', 'PASSED')
        except AssertionError as e:
            log_unittest('CrearRolView', 'test_crear_rol_view_post', 'FAILED')
            raise e

    def test_asignar_permisos_view_get(self):
        """
        Prueba la vista de asignación de permisos en modo GET.
        """
        try:
            response = self.client.get(reverse('asignar_permisos', kwargs={'rol_id': self.rol_editor.id}))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'roles/asignar_permisos.html')
            log_unittest('AsignarPermisosView', 'test_asignar_permisos_view_get', 'PASSED')
        except AssertionError as e:
            log_unittest('AsignarPermisosView', 'test_asignar_permisos_view_get', 'FAILED')
            raise e

    def test_asignar_permisos_view_post(self):
        """
        Prueba la vista de asignación de permisos en modo POST.
        """
        try:
            permiso = Permiso.objects.create(nombre="Nuevo permiso", descripcion="Puede gestionar usuarios")
            post_data = {'permisos': [permiso.id]}
            response = self.client.post(reverse('asignar_permisos', kwargs={'rol_id': self.rol_editor.id}), data=post_data)
            self.assertEqual(response.status_code, 302)
            log_unittest('AsignarPermisosView', 'test_asignar_permisos_view_post', 'PASSED')
        except AssertionError as e:
            log_unittest('AsignarPermisosView', 'test_asignar_permisos_view_post', 'FAILED')
            raise e

    def test_ver_rol_view(self):
        """
        Prueba la vista para ver los permisos de un rol.
        """
        try:
            response = self.client.get(reverse('ver_rol', kwargs={'rol_id': self.rol_editor.id}))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'roles/ver_rol.html')
            self.assertContains(response, "Puede editar contenido")
            log_unittest('VerRolView', 'test_ver_rol_view', 'PASSED')
        except AssertionError as e:
            log_unittest('VerRolView', 'test_ver_rol_view', 'FAILED')
            raise e

    def test_lista_roles_view(self):
        """
        Prueba la vista para listar todos los roles.
        """
        try:
            response = self.client.get(reverse('lista_roles'))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'roles/lista_roles.html')
            self.assertContains(response, "Editor")
            log_unittest('ListaRolesView', 'test_lista_roles_view', 'PASSED')
        except AssertionError as e:
            log_unittest('ListaRolesView', 'test_lista_roles_view', 'FAILED')
            raise e

