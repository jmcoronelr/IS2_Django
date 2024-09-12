from allauth.socialaccount.providers.google.views import oauth2_login
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordChangeView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import RegistroUsuarioForm, UpdateUserForm, UpdateProfileForm

def google_login_redirect(request):
    return oauth2_login(request)

def registrar_usuario(request):
    """
    Vista para registrar un nuevo usuario en el sistema.
    
    Si la solicitud es de tipo POST, se valida el formulario `RegistroUsuarioForm`.
    Si el formulario es válido, el usuario se guarda en la base de datos después de
    configurar su contraseña, y luego se redirige al usuario a la vista de login.
    
    Si la solicitud es GET, se renderiza el formulario vacío.

    Parámetros:
    - request (HttpRequest): Objeto que contiene los datos de la solicitud HTTP.

    Retorna:
    - HttpResponse: Renderiza la plantilla 'usuarios/registro.html' con el formulario
      de registro, o redirige a la vista de login si el registro es exitoso.
    """
    if request.method == 'POST':
        registro_form = RegistroUsuarioForm(request.POST)
        
        if registro_form.is_valid():
            # Crear el usuario
            usuario = registro_form.save(commit=False)
            usuario.set_password(registro_form.cleaned_data['password'])
            usuario.save()
            
            return redirect('usuarios:login')  # Redirige a la vista de login

    else:
        registro_form = RegistroUsuarioForm()

    context = {
        'registro_form': registro_form,
    }
    return render(request, 'usuarios/registro.html', context)

class CustomLoginView(FormView):
    """
    Vista personalizada para el inicio de sesión de usuarios. 
    Utiliza un formulario basado en `AuthenticationForm` para autenticar al usuario.
    
    Atributos:
    - template_name: Nombre de la plantilla a utilizar para renderizar la vista de login.
    - form_class: Clase del formulario que será utilizado (AuthenticationForm).
    - success_url: URL a la que se redirige después de un inicio de sesión exitoso.

    Métodos:
    - form_valid: Si el formulario es válido, autentica y registra al usuario en la sesión.
    """
    template_name = 'usuarios/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('sistema')  # Redirige a la página del sistema tras el login

    def form_valid(self, form):
        """
        Inicia sesión al usuario autenticado si el formulario es válido.

        Parámetros:
        - form (AuthenticationForm): El formulario de autenticación validado.

        Retorna:
        - HttpResponse: Redirige a la URL de éxito definida tras iniciar sesión.
        """
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """
    Vista personalizada para cerrar la sesión del usuario.
    
    Atributos:
    - next_page: URL a la que se redirige después de que el usuario cierra sesión.
    """
    next_page = reverse_lazy('home')  # Redirige a la página principal después del logout


class RecuperarUsuario(SuccessMessageMixin, PasswordResetView):
    """
    Falta añadir comentarios[]][][][][]
    """
    template_name = 'usuarios/password_reset.html'
    email_template_name = 'usuarios/recuperar_usuario_email.html'
    subject_template_name = 'usuarios/recuperar_usuario_asunto.txt'
    success_message = "Te hemos enviado las instrucciones para reinicar tu contraseña, " \
                      "Si existe un usuario con el correo ingresado, deberias recibir el mensaje pronto" \
                      " Si no recibes un correo, " \
                      "asegurate de que ingresaste el correo con el que te registraste y mira la carpeta de spam."
    success_url = reverse_lazy('home')


@login_required
def profile(request):
    """
    Falta añadir comentarios[]][][][][]
    """
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado!')
            return redirect(to='users_profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'usuarios/profile.html', {'user_form': user_form, 'profile_form': profile_form})


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    """
    Falta añadir comentarios[]][][][][]
    """
    template_name = 'usuarios/change_password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('home')