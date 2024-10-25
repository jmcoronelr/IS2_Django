from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class RegistrarUsuarioTests(TestCase):

    def test_registrar_usuario_view_post_failure(self):
        """Verifica que si el formulario es inválido, la página se recargue sin registrar el usuario."""
        datos_usuario = {
            'username': 'nuevo_usuario',
            'email': '',  # El email es obligatorio, así que esto debería fallar
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'password': 'una_contraseña_segura',
        }
        response = self.client.post(reverse('usuarios:registro'), datos_usuario)
        
        self.assertEqual(response.status_code, 200)  # Debería recargar la página
        self.assertTemplateUsed(response, 'usuarios/registro.html')

        # Verificar que el usuario no ha sido creado
        Usuario = get_user_model()
        self.assertFalse(Usuario.objects.filter(username='nuevo_usuario').exists())

class CustomLoginViewTests(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        Usuario = get_user_model()
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_login_view_get(self):
        """Verifica que la vista de login cargue correctamente."""
        response = self.client.get(reverse('usuarios:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')

    def test_login_view_post_success(self):
        """Verifica que un usuario pueda iniciar sesión exitosamente."""
        response = self.client.post(reverse('usuarios:login'), {
            'username': self.user.email,
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('sistema'))  # Redirección a la página de sistema

    def test_login_view_post_failure(self):
        """Verifica que un usuario no pueda iniciar sesión con credenciales incorrectas."""
        response = self.client.post(reverse('usuarios:login'), {
            'username': self.user.email,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Debería recargar la página
        self.assertTemplateUsed(response, 'usuarios/login.html')

class CustomLogoutViewTests(TestCase):
    def setUp(self):
        # Crear un usuario de prueba y loguearlo
        Usuario = get_user_model()
        self.user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.client.login(username=self.user.email, password='testpassword')

    def test_logout_view(self):
        """Verifica que el usuario pueda cerrar sesión exitosamente."""
        response = self.client.post(reverse('usuarios:logout'))
        self.assertRedirects(response, reverse('home'))  # Redirección a la página de inicio