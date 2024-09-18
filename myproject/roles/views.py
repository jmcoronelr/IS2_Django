from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, Rol, RolEnCategoria, Categorias, Permiso
from .forms import AsignarRolForm, CrearRolForm, AsignarPermisoForm

@login_required
def asignar_rol(request, usuario_id):
    """
    Asigna o actualiza un rol para un usuario en una categoría específica.
    Si el método es POST, se procesa el formulario y se asigna un rol.
    Si el método es GET, se muestra el formulario para la asignación.
    
    :param request: La solicitud HTTP.
    :param usuario_id: El ID del usuario al que se le va a asignar el rol.
    :return: Renderiza la plantilla de asignación de roles.
    """
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
    """
    Muestra los roles asignados a un usuario en diferentes categorías.

    :param request: La solicitud HTTP.
    :param usuario_id: El ID del usuario cuyos roles serán mostrados.
    :return: Renderiza la plantilla que muestra los roles y categorías del usuario.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    roles_en_categoria = RolEnCategoria.objects.filter(usuario=usuario)
    return render(request, 'roles/ver_usuario.html', {
        'usuario': usuario,
        'roles_en_categoria': roles_en_categoria,
    })

@login_required
def lista_usuarios(request):
    """
    Lista todos los usuarios del sistema.

    :param request: La solicitud HTTP.
    :return: Renderiza la plantilla que muestra la lista de usuarios.
    """
    query = request.GET.get('q')
    if query:
        usuarios = Usuario.objects.filter(email__icontains=query)
    else:
        usuarios = Usuario.objects.all()
    return render(request, 'roles/lista_usuarios.html', {'usuarios': usuarios})

@login_required
def crear_rol(request):
    """
    Crea un nuevo rol en el sistema.

    :param request: La solicitud HTTP.
    :return: Renderiza la plantilla con el formulario de creación de roles.
    """
    if request.method == 'POST':
        form = CrearRolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'El rol ha sido creado correctamente.')
            return redirect('lista_roles')  # Asume que tienes una vista de lista de roles
    else:
        form = CrearRolForm()

    return render(request, 'roles/crear_rol.html', {'form': form})

@login_required
def asignar_permisos(request, rol_id):
    """
    Asigna permisos a un rol específico.

    :param request: La solicitud HTTP.
    :param rol_id: El ID del rol al que se le asignarán permisos.
    :return: Renderiza la plantilla con el formulario de asignación de permisos.
    """
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
    """
    Muestra los detalles de un rol, incluidos los permisos asignados.

    :param request: La solicitud HTTP.
    :param rol_id: El ID del rol que se va a mostrar.
    :return: Renderiza la plantilla que muestra los permisos del rol.
    """
    rol = get_object_or_404(Rol, id=rol_id)
    permisos = rol.permisos.all()  # Obtenemos los permisos asignados al rol
    return render(request, 'roles/ver_rol.html', {
        'rol': rol,
        'permisos': permisos,
    })

@login_required
def lista_roles(request):
    """
    Lista todos los roles disponibles en el sistema.

    :param request: La solicitud HTTP.
    :return: Renderiza la plantilla que muestra la lista de roles.
    """
    query = request.GET.get('q')
    if query:
        roles = Rol.objects.filter(nombre__icontains=query)
    else:
        roles = Rol.objects.all()  # Obtenemos todos los roles
    return render(request, 'roles/lista_roles.html', {
        'roles': roles,
    })

@login_required
def eliminar_rol(request, rol_id):
    """ Eliminar un rol con confirmación previa """
    rol = get_object_or_404(Rol, id=rol_id)
    
    if request.method == 'POST':
        rol.delete()
        messages.success(request, f'El rol {rol.nombre} ha sido eliminado exitosamente.')
        return redirect('lista_roles')
    
    return render(request, 'roles/confirmar_eliminar.html', {'rol': rol})

