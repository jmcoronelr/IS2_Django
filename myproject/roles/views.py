from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Usuario, Rol, RolEnCategoria, Categorias, Permiso
from .forms import AsignarRolForm, CrearRolForm, AsignarPermisoForm
from django.urls import reverse
from django.core.exceptions import ValidationError

@login_required
def asignar_rol(request, usuario_id):
    """
    Asigna o actualiza un rol para un usuario en una categoría específica.
    Si el método es POST, se procesa el formulario y se asigna un rol.
    Si el método es GET, se muestra el formulario para la asignación.
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
    """
    rol = get_object_or_404(Rol, id=rol_id)
    
    # Obtener la URL anterior (referencia)
    previous_url = request.META.get('HTTP_REFERER', reverse('lista_roles'))  # Si no hay HTTP_REFERER, redirige a lista_roles por defecto.
    
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
        'form': form,
        'previous_url': previous_url,  # Pasar la URL anterior al template
    })

@login_required
def ver_rol(request, rol_id):
    """
    Muestra los detalles de un rol, incluidos los permisos asignados.

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
        try:
            # Intentamos eliminar el rol
            rol.delete()
            messages.success(request, f'El rol {rol.nombre} ha sido eliminado exitosamente.')
        except ValidationError as e:
            # Capturamos el error y mostramos el mensaje al usuario
            messages.error(request, e.message)
        return redirect('lista_roles')
    
    return render(request, 'roles/confirmar_eliminar.html', {'rol': rol})

@login_required
def eliminar_rol_en_categoria(request, rol_en_categoria_id):
    """
    Eliminar un rol específico asignado a un usuario en una categoría.
    """
    rol_en_categoria = get_object_or_404(RolEnCategoria, id=rol_en_categoria_id)

    if request.method == 'POST':
        rol_en_categoria.delete()
        #messages.success(request, f'El rol {rol_en_categoria.rol.nombre} en la categoría {rol_en_categoria.categoria.descripcionCorta} ha sido eliminado correctamente.')
        return redirect('ver_usuario', usuario_id=rol_en_categoria.usuario.id)
    
    return render(request, 'roles/confirmar_eliminar.html', {'rol_en_categoria': rol_en_categoria})