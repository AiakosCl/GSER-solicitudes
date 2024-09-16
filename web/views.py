from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from web.models import *
from web.forms import *
# Create your views here.

iconos = {
    'ok':'👌🏼',
    'mal':'👎🏼'
}

class Login(LoginView):
    template_name="registration/login.html"

class Logout(LogoutView):
    next_page="/"

# -- Funciones auxiliares -- #

def index(request):

    return render(request, 'index.html', {})



#Vista Trabajo Usuarios
def nuevo_usuario(request):
    gerencias = Gerencia.objects.all().order_by('descripcion')
    perfiles = Perfiles.objects.all()
    next_url = request.GET.get('next')

    if request.method=='POST':
        formulario = NuevoUsuarioForm(request.POST)
        print(request.POST.get('ceco_id'))
        if formulario.is_valid():
            try:
                usuario = formulario.save(commit=False)
                usuario.save()
                # login(request, usuario) #Para iniciar sesión automáticamente, si se desea.
                messages.success(request, f'{iconos["ok"]}\t¡Se ha registrado al nuevo usuario!')
                if request.user.is_authenticated:
                    if request.user.is_staff:
                        return redirect('Ficha', usuario_id=usuario.id)
                    else:
                        return redirect('inicio')
                else:
                    return redirect('login')
            except ValueError as e:
                messages.error(request, f'{iconos["mal"]}\tError al crear el usuario: {str(e)}')
        else:
            messages.warning(request,f'{iconos["mal"]}\tUps! Algo salió mal. Revisar la inforamción ingresada.')
    else:
        formulario = NuevoUsuarioForm()

    contexto={
        'formulario':formulario,
        'gerencias':gerencias,
        'perfiles':perfiles
    }
    
    return render(request, 'usuario_nuevo.html', contexto)

@login_required
def lista_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'lista_usuarios.html',{'lista':usuarios})

@login_required
def vista_ficha(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    return render(request, 'detalle_usuario.html', {'usuario':usuario})

@login_required
def editar_usuario(request, usuario_id):
    next_url = request.GET.get('next')
    gerencias = Gerencia.objects.all().order_by('descripcion')
    perfiles = Perfiles.objects.all()

    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return "Usuario no Existe"
    

    if request.method == 'POST':
        usuario.first_name=request.POST.get('first_name', usuario.first_name)
        usuario.last_name = request.POST.get('last_name', usuario.last_name)
        usuario.email = request.POST.get('email', usuario.email)
        usuario.telefono = request.POST.get('telefono', usuario.telefono)
        
        gerencia_id = request.POST.get('ceco_id')
        print(gerencia_id)
        if gerencia_id:
            print(gerencia_id)
            gerencia = get_object_or_404(Gerencia, ceco=gerencia_id)
            usuario.ceco_id = gerencia

        if request.user.is_superuser or request.user.is_staff:
            usuario.rut = request.POST.get('rut', usuario.rut)
            perfil_id = request.POST.get('tipo_usuario')
            if perfil_id:
                usuario.tipo_usuario_id = perfil_id
            
            usuario.is_staff = request.POST['is_staff']
            usuario.is_active = request.POST['is_active']
        
        if request.POST['password']:
            usuario.set_password(request.POST['password']) #set_password establece una password encriptada para la tabla User

        usuario.save()
        
        messages.success(request, f'{iconos["ok"]}\t¡Actualización de datos correcta!')
        
        if request.user.is_superuser or request.user.is_staff: 
            return redirect('ListaUsuarios')
        else:
            return redirect('Ficha', usuario_id=usuario.id)
        
    contexto = {
        'formulario':usuario,
        'next_url':next_url,
        'gerencias':gerencias,
        'perfiles':perfiles
    }
    
    return render(request, 'usuario_editar.html', contexto)

@login_required
def eliminar_usuario(request, usuario_id):
    if request.user.is_superuser or request.user.is_staff:    
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
        except Usuario.DoesNotExist:
            return "Usuario no existe"
        
        if request.method == 'POST':
            usuario.delete()
            messages.success(request, f'{iconos["ok"]}\t¡Se ha eliminado el usuario!')
            return redirect('ListaUsuarios')
        
        return render(request, 'usuario_eliminar.html', {'usuario':usuario})
    else:
        messages.warning(request,f'{iconos["mal"]}\tUsted no está autorizado para esta operación')
        return redirect('inicio')

@login_required    
def filtrarUsuarios(request):
    termino = request.GET.get('q')
    usuarios = Usuario.objects.all()

    if termino:
        usuarios = usuarios.filter(
            Q(first_name__icontains=termino)|Q(last_name__icontains=termino)
        )
    
    return render(request, 'lista_usuarios.html',{'lista':usuarios})

