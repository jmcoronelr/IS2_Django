from pyexpat.errors import messages
from django.forms import ValidationError
from django.shortcuts import redirect, render
from .forms import AsignarRolForm, RegistroUsuarioForm
from .models import Rol, Usuario, UsuarioRol
from django.core.exceptions import ValidationError
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
    
def asignar_rol(usuario, rol): # Funcion encargada de asignar el rol a un usuario
    roles_actuales = UsuarioRol.objects.filter(usuario=usuario).count()
    if roles_actuales >= 2:
        raise ValidationError("Un usuario no puede tener más de 2 roles.")
    UsuarioRol.objects.get_or_create(usuario=usuario, rol=rol)


def asignar_roles(request): # Form para asignar rol
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        rol_id = request.POST.get('rol_id')
        
        usuario = Usuario.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        
        try:
            asignar_rol(usuario, rol)
            messages.success(request, "Rol asignado exitosamente.")
        except ValidationError as e:
            messages.error(request, str(e))

    return redirect('some_view')

def registrar_usuario(request):
    if request.method == 'POST':
        registro_form = RegistroUsuarioForm(request.POST)
        rol_form = AsignarRolForm(request.POST)
        
        if registro_form.is_valid():
            # Crear el usuario
            usuario = registro_form.save(commit=False)
            usuario.set_password(registro_form.cleaned_data['password'])
            usuario.save()

            # Asignar rol si el formulario de rol es válido
            if rol_form.is_valid():
                usuario_rol = rol_form.cleaned_data['usuario']
                rol = rol_form.cleaned_data['rol']
                try:
                    asignar_rol(usuario_rol, rol)
                    messages.success(request, 'Rol asignado exitosamente.')
                except ValidationError as e:
                    messages.error(request, str(e))
            
            return redirect('login')  # Redirige a la página de inicio o a cualquier otra vista

    else:
        registro_form = RegistroUsuarioForm()
        rol_form = AsignarRolForm()

    context = {
        'registro_form': registro_form,
        'rol_form': rol_form
    }
    return render(request, 'registro.html', context)




class CustomLoginView(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('sistema')  # Redirige a la página de inicio después de iniciar sesión

    def form_valid(self, form):
        # Inicia sesión al usuario y redirige a la página de inicio
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)
