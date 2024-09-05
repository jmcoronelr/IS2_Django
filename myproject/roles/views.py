from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, Rol, RolEnCategoria, Categorias
from .forms import AsignarRolForm

@login_required
def asignar_rol(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    roles_actuales = RolEnCategoria.objects.filter(usuario=usuario)
    
    try:
        if request.method == 'POST':
            form = AsignarRolForm(request.POST)
            if form.is_valid():
                categoria = form.cleaned_data['categoria']
                rol = form.cleaned_data['rol']
                # Crear o actualizar el RolEnCategoria
                RolEnCategoria.objects.update_or_create(
                    usuario=usuario, 
                    categoria=categoria, 
                    defaults={'rol': rol}
                )
                messages.success(request, 'Rol asignado correctamente.')
                return redirect('ver_usuario', usuario_id=usuario.id)
        else:
            form = AsignarRolForm()
    except Exception as e:
        # Muestra el error en consola
        print(f"Error: {e}")
        messages.error(request, "Ocurrió un error inesperado.")
        form = AsignarRolForm()

    return render(request, 'roles/asignar_rol.html', {
        'usuario': usuario,
        'form': form,
        'roles_actuales': roles_actuales
    })

@login_required
def ver_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    roles_en_categoria = RolEnCategoria.objects.filter(usuario=usuario)
    return render(request, 'roles/ver_usuario.html', {
        'usuario': usuario,
        'roles_en_categoria': roles_en_categoria,
    })

@login_required
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'roles/lista_usuarios.html', {'usuarios': usuarios})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Rol
from .forms import CrearRolForm

@login_required
def crear_rol(request):
    if request.method == 'POST':
        form = CrearRolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El rol ha sido creado correctamente.')
            return redirect('lista_roles')  # Asume que tienes una vista de lista de roles
    else:
        form = CrearRolForm()

    return render(request, 'roles/crear_rol.html', {'form': form})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Permission
from .models import Rol
from .forms import AsignarPermisoForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Rol, Permiso
from .forms import AsignarPermisoForm

@login_required
def asignar_permisos(request, rol_id):
    rol = get_object_or_404(Rol, id=rol_id)
    if request.method == 'POST':
        form = AsignarPermisoForm(request.POST, instance=rol)
        if form.is_valid():
            permisos = form.cleaned_data['permisos']
            rol.permisos.set(permisos) 
            rol.save()
            messages.success(request, f'Se han asignado permisos al rol {rol.nombre}.')
            return redirect('ver_rol', rol_id=rol.id)
    else:
        form = AsignarPermisoForm(instance=rol)

    return render(request, 'roles/asignar_permisos.html', {
        'rol': rol,
        'form': form
    })

@login_required
def ver_rol(request, rol_id):
    rol = get_object_or_404(Rol, id=rol_id)
    permisos = rol.permisos.all()  # Obtenemos los permisos asignados al rol
    return render(request, 'roles/ver_rol.html', {
        'rol': rol,
        'permisos': permisos,
    })

@login_required
def lista_roles(request):
    roles = Rol.objects.all()  # Obtenemos todos los roles
    return render(request, 'roles/lista_roles.html', {
        'roles': roles,
    })
