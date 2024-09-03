from pyexpat.errors import messages
from django.shortcuts import redirect, render
from .forms import RegistroUsuarioForm
from django.views.generic.edit import FormView
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
    

def registrar_usuario(request):
    if request.method == 'POST':
        registro_form = RegistroUsuarioForm(request.POST)
        
        if registro_form.is_valid():
            # Crear el usuario
            usuario = registro_form.save(commit=False)
            usuario.set_password(registro_form.cleaned_data['password'])
            usuario.save()

            
            return redirect('usuarios:login')  # Redirige a la página de inicio o a cualquier otra vista

    else:
        registro_form = RegistroUsuarioForm()

    context = {
        'registro_form': registro_form,
    }
    return render(request, 'usuarios/registro.html', context)




class CustomLoginView(FormView):
    template_name = 'usuarios/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('sistema')  # Redirige a la página de inicio después de iniciar sesión

    def form_valid(self, form):
        # Inicia sesión al usuario y redirige a la página de inicio
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')  # Redirige a la página de login después del logout