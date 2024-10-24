from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.urls import reverse_lazy
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
    areas_servicios = AreaServicio.objects.all()
    return render(request, 'index.html', {'areas': areas_servicios})

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


# Trabajo con Servicios #

@login_required
def lista_servicios(request, area_servicio_id):
    disponibles = Servicio.objects.filter(area_servicio = area_servicio_id)
    return render(request, 'lista_servicios.html', {'lista':disponibles})

@login_required
def ver_solicitudes_lavanderia(request): #Mejorar la opciones de vista
    return render(request, 'lista_lavanderia.html')

@login_required
def ticket_lavanderia(request):
    prendas = Servicio.objects.filter(area_servicio = 4)
    
    try:
        locker_asignado = Lockers.objects.get(usuario_locker=request.user)

    except Lockers.DoesNotExist:
        locker_asignado = None

    if locker_asignado is None:
        messages.warning(request, 'Debe asignar un locker para poder realizar el pedido')
        return redirect('asignar_locker')
    
    if request.method == 'POST':
        formulario = TicketLavanderiaForm(request.POST)
    
    return render(request, 'solicitar_lavanderia.html', {'prendas':prendas, 'locker':locker_asignado})

@login_required
def asignar_locker(request):
    if request.method == 'POST':
        numero_locker = request.POST.get('numero_locker')
        lugar_trabajo = request.POST.get('lugar_trabajo')
        casacambio = request.POST.get('casacambio')

        try:
            locker_asignado = Lockers.objects.get(
                numero_locker = numero_locker,
                lugar_trabajo = lugar_trabajo,
                casacambio_id = casacambio
            )
            if locker_asignado.usuario_locker is None:
                locker_asignado.usuario_locker = request.user
                locker_asignado.save()
                messages.success(request, 'Locker asignado correctamente')
                return redirect('ticket_lavanderia')
            else:
                messages.error(request, 'Locker ya asignado')
        
        except Lockers.DoesNotExist:
            messages.error(request, "Locker no encontrado o incorrecto")
            locker_asignado = None

        if locker_asignado is None:
            messages.warning(request, 'No hay lockers disponibles para asignar')

    return render(request, 'asignar_locker.html')

# ---- Trabajo con Carrito ------ #

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Servicio, id_producto = producto_id)
    carrito, created = Carrito.objects.get_or_create(usuario = request.user)
    elemento, created = ItemsCarrito.objects.get_or_create(carrito=carrito, producto=producto)

    if not created:
        elemento.cantidad += 1
        elemento.save()

    return redirect('ver_carrito')

# Muestra el carrito
@login_required
def ver_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    elementos = ItemsCarrito.objects.filter(carrito=carrito)

    total = 0
    for elemento in elementos:
        elemento.subtotal = elemento.producto.precio * elemento.cantidad
        total += elemento.subtotal

    return render(request, 'carrito.html', {'carrito':carrito, 'elementos':elementos, 'total':total})

# Eliminar una línea del Carrito
@login_required
def eliminar_item_carrito(request, elemento_id):
    elemento = get_object_or_404(ItemsCarrito, id=elemento_id)

    if request.user == elemento.carrito.usuario:
        elemento.delete()
    
    return redirect('ver_carrito')

# Aumenta en 1 el pedido del item de la línea
@login_required
def aumentar_item(request, elemento_id):
    elemento = get_object_or_404(ItemsCarrito, id=elemento_id)

    if request.user == elemento.carrito.usuario:
        elemento.cantidad += 1
        elemento.save()
    
    return redirect('ver_carrito')

# Disminuye en 1 el pedido del item de la línea
@login_required
def disminuir_item(request, elemento_id):
    elemento = get_object_or_404(ItemsCarrito, id=elemento_id)

    if request.user == elemento.carrito.usuario:
        if elemento.cantidad <=0:
            elemento.cantidad = 1
        else:
            elemento.cantidad -=1

        elemento.save()

    return redirect('ver_carrito')

# Varciar el registro en Carrito
@login_required
def vaciar_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    elementos = ItemsCarrito.objects.filter(carrito=carrito)
    carrito.delete()
    return redirect('inicio')

# Realizar el pedido
@login_required
def realizar_pedido(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    elementos = ItemsCarrito.objects.filter(carrito=carrito)
    
    with transaction.atomic():
        pedido = Pedido.objects.create(usuario=request.user, total=0)

        total = 0

        for elemento in elementos:
            subtotal = elemento.producto.precio * elemento.cantidad
            total += subtotal

            DetallePedido.objects.create(
                pedido = pedido,
                producto = elemento.producto,
                cantidad = elemento.cantidad,
                precio = elemento.producto.precio
            )

            pedido.total = total
            pedido.save()

    Correo = '''
    # Armando el correo electrónico
    asunto = f'Confirmación pedido: {carrito.id}'
    mensaje_html = render_to_string('confirmacion_pedido.html', {'elementos':elementos})
    mensaje_texto = strip_tags(mensaje_html)

    email = EmailMessage(
        asunto,
        mensaje_texto,
        'only.flans@gmail.com',
        [request.user.email],
    )

    # Generar PDF adjunto
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    elementos_tabla = []
    
    # Estilos para el PDF
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(name='Titulo', fontSize=16, spaceAfter=20)
    estilo_encabezado = ParagraphStyle(name='Encabezado', fontSize=12, spaceAfter=10)
    estilo_texto = ParagraphStyle(name='Texto', fontSize=10, spaceAfter=5)
    
    # Agregar título al PDF
    titulo = Paragraph('Confirmación de Pedido', estilo_titulo)
    elementos_tabla.append(titulo)
    
    # Agregar detalles del pedido al PDF
    detalles = Paragraph(f'Pedido realizado por: {request.user.username}', estilo_texto)
    elementos_tabla.append(detalles)
    
    # Agregar tabla de productos al PDF
    encabezados = ['Producto', 'Cantidad', 'Precio Unitario', 'Subtotal']
    datos_tabla = [encabezados]
    
    total = 0
    for elemento in elementos:
        subtotal = elemento.producto.precio * elemento.cantidad
        total += subtotal
        fila = [elemento.producto.nombre, str(elemento.cantidad), str(elemento.producto.precio), str(subtotal)]
        datos_tabla.append(fila)
    
    tabla = Table(data=datos_tabla)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elementos_tabla.append(tabla)
    
    # Agregar total al PDF
    total_texto = Paragraph(f'Total: {total}', estilo_texto)
    elementos_tabla.append(total_texto)
    
    pdf.build(elementos_tabla)
    buffer.seek(0)

    email.attach('confirmacion_pedido.pdf', buffer.getvalue(), 'application/pdf')

    email.send()
'''

    messages.success(request, f'{iconos["ok"]}\t¡Hemos recibido su pedido! Esté atento a su correo.')
    carrito.delete()
    return redirect('/')

def historial(request):
    pass

# --- Valoración de Servicios --- #

@login_required
def valorar_servicios(request, servicio_id):
    modelo = int(servicio_id.split('-')[0])
    
    # Validación si el área de servicio existe y obtiene su nombre y clase, si no, redireccionar a inicio
    try:
        area_servicio = AreaServicio.objects.get(pk=modelo)
        servicio_model = apps.get_model('web', area_servicio._meta.model_name) # Obtener el modelo del area de servicio (nombre y clase)
        servicio_instance = servicio_model.objects.get(pk=servicio_id)
    except (AreaServicio.DoesNotExist, servicio_model.DoesNotExist) as e: # Valida si tanto el área de servicio como el modelo existen
        messages.error(request, f'{iconos["mal"]}\tClase de Servicio no encontrado')
        return redirect('inicio')
    except servicio_instance.DoesNotExist: # Valida si el requeriminto o solicitud existe
        messages.error(request, f'{iconos["mal"]}\tRequerimiento/Solicitud no existe')
        return redirect('inicio')

    # Crear valoración
    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        comentario = request.POST.get('comentario')

        content_type = ContentType.objects.get_for_model(servicio_instance)
        valoracion = Valoracion.objects.create(
            content_type=content_type,
            object_id=servicio_instance.id,
            calificacion=calificacion,
            comentario=comentario
        )

        valoracion.save()

        messages.success(request, f'{iconos["ok"]}\t¡Gracias por valorar el servicio!')

        return redirect('inicio')
    
    return render(request, 'valorar_servicio.html', {'servicio':servicio_instance})

def mostrar_valoraciones(request, servicio_id, servicio_model):
    servicio_instance = servicio_model.objects.get(id=servicio_id)
    content_type = ContentType.objects.get_for_model(servicio_instance)

    # Obtener todas las valoraciones de este servicio
    valoraciones = Valoracion.objects.filter(content_type=content_type, object_id=servicio_instance.id)

    return render(request, 'mostrar_valoraciones.html', {'servicio': servicio_instance, 'valoraciones': valoraciones})


# --- Trabajo con Contacto Sugerencias --- #

@login_required
def contacto(request):
    usuario = Usuario.objects.get(id=request.user.id)
    areas = AreaServicio.objects.all()

    if request.method == 'POST':
        formulario = ContactoForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, f'{iconos["ok"]}\t¡Gracias por contactarnos!')
            return redirect('inicio')
        else:
            messages.warning(request, f'{iconos["mal"]}\tUps! Algo salió mal. Revisar la inforamción ingresada.')
    else:
        formulario = ContactoForm()

    return render(request, 'contacto.html', {'formulario': formulario, 'usuario': usuario,'areas': areas}) 
