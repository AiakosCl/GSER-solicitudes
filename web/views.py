from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Sum
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from datetime import datetime, date
import pytz
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
    show_cart = request.GET.get('show_cart', False)
    vista = request.GET.get('vista', False)
    if not vista:
        vista = 'inicio'

    if request.user.is_authenticated:
        areas_servicios = request.user.servicio_autorizado.all().order_by('id')
        carrito = Carrito.objects.filter(usuario=request.user).first()
        elementos = ItemsCarrito.objects.filter(carrito=carrito)
        
        try:
            locker = Lockers.objects.get(usuario_locker=request.user)
        except Lockers.DoesNotExist:
            locker = None

        total = 0
        for elemento in elementos:
            try:
                elemento.subtotal = elemento.producto.precio * elemento.cantidad
            except:
                elemento.subtotal = 0

            vista=elemento.producto.area_servicio.vista
            print(vista)
            total += elemento.subtotal

        return render(request, 'index.html', {
            'areas': areas_servicios, 
            'vista':vista, 
            'carrito':carrito, 
            'elementos':elementos, 
            'total':total,
            'show_cart':show_cart,
            'locker':locker
        })
    else:
        areas_servicios = AreaServicio.objects.all().order_by('id')
    return render(request, 'index.html', {'areas': areas_servicios, 'vista':vista, 'show_cart':show_cart})

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
    areas = Area.objects.all()
    if request.method == 'POST':
        formulario = LockerAssignmentForm(request.POST)
        if formulario.is_valid():
            numero_locker = formulario.cleaned_data['numero_locker']
            lugar_trabajo = formulario.cleaned_data['lugar_trabajo']
            casacambio = formulario.cleaned_data['casacambio']

            try:
                # Verificamos si el locker está disponible
                locker_asignado = Lockers.objects.get(
                    numero_locker=numero_locker,
                    lugar_trabajo=lugar_trabajo,
                    casacambio=casacambio
                )
                if locker_asignado.usuario_locker is None:
                    locker_asignado.usuario_locker = request.user
                    locker_asignado.save()
                    messages.success(request, f'{iconos["ok"]}\tLocker asignado correctamente')
                    return redirect('lavanderia')
                else:
                    messages.error(request, f'{iconos["mal"]}\tLocker ya está asignado a otro usuario')
            except Lockers.DoesNotExist:
                messages.error(request, f'{iconos["mal"]}\tLocker no encontrado o incorrecto')
    else:
        formulario = LockerAssignmentForm()
    
    contexto = {
        'formulario':formulario,
        'areas':areas
    }

    return render(request, 'asignar_locker.html', contexto)

def cargar_casascambio(request, area_id):
    casas = SalasCambio.objects.filter(area=area_id).values('id', 'nombre_sala')
    return JsonResponse(list(casas), safe=False)

def cargar_lockers(request, casacambio_id):
    lockers = Lockers.objects.filter(casacambio=casacambio_id, usuario_locker=None).values('id', 'numero_locker')
    return JsonResponse(list(lockers), safe=False)



# ---- Trabajo con Carrito ------ #

@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Servicio, id = producto_id)
    carrito, created = Carrito.objects.get_or_create(usuario = request.user, area_servicio = producto.area_servicio)
    elemento, created = ItemsCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    servicio = producto.area_servicio_id
    vista = AreaServicio.objects.get(id=servicio).vista

    if not created:
        elemento.cantidad += 1
        elemento.save()

    messages.success(request, f'{iconos["ok"]}\t{producto.nombre_servicio} se agregó al carrito')
    return redirect(reverse('inicio')+ f'?vista={vista}&show_cart=True')
    # return redirect(reverse('ver_carrito')+ f'?vista={vista}')

# Muestra el carrito
@login_required
def ver_carrito(request):
    vista = request.GET.get('vista')
    carrito = Carrito.objects.filter(usuario=request.user).first()
    elementos = ItemsCarrito.objects.filter(carrito=carrito)
    total = 0
    for elemento in elementos:
        try:
            elemento.subtotal = elemento.producto.precio * elemento.cantidad

        except:
            elemento.subtotal = 0

        total += elemento.subtotal

    return render(request, 'carrito_offcanva.html', {'carrito':carrito, 'elementos':elementos, 'total':total, 'vista':vista})

# Eliminar una línea del Carrito
@login_required
def eliminar_item_carrito(request, elemento_id):
    vista = request.GET.get('vista')
    elemento = get_object_or_404(ItemsCarrito, id=elemento_id)

    if request.user == elemento.carrito.usuario:
        elemento.delete()
    
    messages.info(request, f'{iconos["mal"]}\tSe eliminó línea del carrito')
    return redirect(reverse('inicio')+ f'?vista={vista}&show_cart=True')
    #return redirect(reverse('ver_carrito')+ f'?vista={vista}')

# Aumenta en 1 el pedido del item de la línea
@login_required
def aumentar_item(request, elemento_id):
    vista = request.GET.get('vista')
    elemento = get_object_or_404(ItemsCarrito, id=elemento_id)

    if request.user == elemento.carrito.usuario:
        elemento.cantidad += 1
        elemento.save()
    return redirect(reverse('inicio')+ f'?vista={vista}&show_cart=True')
    #return redirect(reverse('ver_carrito')+ f'?vista={vista}')

# Disminuye en 1 el pedido del item de la línea
@login_required
def disminuir_item(request, elemento_id):
    vista = request.GET.get('vista')
    elemento = get_object_or_404(ItemsCarrito, id=elemento_id)

    if request.user == elemento.carrito.usuario:
        if elemento.cantidad <=0:
            elemento.cantidad = 1
        else:
            elemento.cantidad -=1

        elemento.save()

    return redirect(reverse('inicio')+ f'?vista={vista}&show_cart=True')
    #return redirect(reverse('ver_carrito')+ f'?vista={vista}')

# Varciar el registro en Carrito
@login_required
def vaciar_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    elementos = ItemsCarrito.objects.filter(carrito=carrito)
    carrito.delete()
    messages.warning(request, 'Se ha vaciado el carrito')
    return redirect(reverse('inicio')+'#contenido')


@login_required    
def filtrar_articulos(request):
    termino = request.GET.get('q')
    articulos = Servicio.objects.all()

    if termino:
        articulos = articulos.filter(Q(nombre_servicio__icontains=termino))
    
    return render(request, 'lavanderia.html',{'servicios':articulos})


# Realizar el pedido
@login_required
def realizar_pedido(request):
    # Obtiene los iconos

    iconos = {
        'solicitud': IconosBase64.objects.get(icono='solicitud').icono_base64,
        'recepcion': IconosBase64.objects.get(icono='recepcion').icono_base64,
        'revision': IconosBase64.objects.get(icono='revision').icono_base64,
        'proceso': IconosBase64.objects.get(icono='proceso').icono_base64,
        'completo': IconosBase64.objects.get(icono='completo').icono_base64,
    }

    # Obtiene el carrito del usuario actual
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if not carrito: #Verifica si existe un carrito
        messages.error(request, f'{iconos["mal"]}\tNo existe carrito relacionado a este Usuario')
        return redirect('/')

    elementos = ItemsCarrito.objects.filter(carrito=carrito)
    if not elementos.exists(): #Verifica si el carro tiene elementos
        messages.error(request, f'{iconos["mal"]}\tNo tienes artículos en el carrito.')
        return redirect('/')
    else:
        detalle = "\n".join([f" - {elemento.producto} x {elemento.cantidad}" for elemento in elementos])

    try:
        with transaction.atomic():
            # Crear el pedido
            pedido = Pedido.objects.create(
                usuario=request.user,
                fecha_creacion = datetime.now(pytz.timezone('America/Santiago')), # Se obtiene la fecha y hora actual y localiza la zona horaria de Chile
                area_servicio=carrito.area_servicio,  # Se obtiene el Id de servicio de la tabla Carrito
                ceco=request.user.ceco_id,  # Asignar el CECO del usuario. Se obtiene de la Tabla Usuario
                total=0,  # Inicialmente cero, se calculará más adelante
            )

            total = 0

            # Iterar sobre los elementos del carrito
            for elemento in elementos:
                subtotal = (elemento.producto.precio_servicio if elemento.producto.precio_servicio else 0) * elemento.cantidad
                total += subtotal

                # Crear detalle del pedido
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=elemento.producto,
                    cantidad=elemento.cantidad,
                    precio=elemento.producto.precio_servicio
                )

            # Asignar el total calculado al pedido
            pedido.total = total
            pedido.save()
        
        # Notificaciones

        # Enviar correo de HTML

        asunto = f'Solicitud de {carrito.area_servicio.nombre_area}: {pedido.id}'
        destinatarios = [request.user.email,'galva026@contratistas.codelco.cl']

        cuerpo = {
            'linea1': f"Esta es una notificación automática para confirmar que hemos registrado tu solicitud de {carrito.area_servicio.nombre_area.upper()}.",
            'linea2': "Cualquier cambio de estado de la misma será informada por este medio. Sin embargo, tambien podrás consultar el estado a través de la aplicación en 'Mis Solicitudes'.",

        }
        
        # Correo HTML
        avance = 20
        mensaje_html = render_to_string('confirmacion.html', {'pedido': pedido, 'usuario': request.user, 'elementos':elementos, 'avance':avance, 'iconos':iconos,'contenido':cuerpo})
        email = EmailMessage(
            asunto,
            mensaje_html,
            settings.DEFAULT_FROM_EMAIL,
            destinatarios,
        )
        email.content_subtype = 'html'
        email.send()
        
        correo_texto = """
        #Correo Texto
        # mensaje = f'''
        # Estimado(a) {request.user.first_name}:
        
        # Hemos registrado tu solicitud de {carrito.area_servicio.nombre_area}.

        # Para tu conocimiento el proceso sería:

        # Solicitud -> Recogida -> Revisión -> Confirmación -> Lavado -> Entrega
        
        # Detalle de tu solicitud:

        # ID: {pedido.id}
        # Fecha de solicitud: {pedido.fecha_creacion.strftime('%d-%m-%Y %H:%M')}
        # Area de Servicio: {pedido.area_servicio.nombre_area}
        # CECO: {pedido.ceco}

        #     Artículos enviados:    
        #     {detalle}

        # Total: {pedido.total}


        # Gracias por utilizar nuestros servicios.

        
        # Atentamente,
        # Gestión de Servicios SSP

        # **Esto es sólo una notificación automática. No responder a este correo.**
        # '''
        # send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL,destinatarios)
"""
        
        # Eliminar el carrito y los elementos
        elementos.delete()
        carrito.delete()
        
        # Mensaje de éxito
        messages.success(request, '¡Hemos recibido su pedido! Esté atento a su correo.')
    except Exception as e: #Si hubiera algún error...
        messages.error(request, f'Error al procesar el pedido: {str(e)}')

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
            messages.error(request, f'{iconos["mal"]}\tUps! Algo salió mal. Revisar la información ingresada o faltante.')
    else:
        formulario = ContactoForm()

    return render(request, 'contacto.html', {'formulario': formulario, 'usuario': usuario,'areas': areas}) 


# ---- Trabajo con Solicitud de servicios ------ #

@login_required
def solicitar(request, id_areaservicio):

    try:
        servicio = AreaServicio.objects.get(id=id_areaservicio)
    except AreaServicio.DoesNotExist:
        messages.error(request, f'{iconos["mal"]}\tArea de Servicio no encontrada')
        return redirect('inicio')

@login_required
def alimentacion(request):
    return render(request, 'alimentacion.html')

@login_required
def hoteleria(request):
    return render(request, 'hoteleria.html')

@login_required
def lavanderia(request):
    productos = Servicio.objects.filter(area_servicio = 4)
    vista = "lavanderia"
    
    try:
        locker = Lockers.objects.get(usuario_locker=request.user)
    except Lockers.DoesNotExist:
        #Se debe hacer una rutina para permitir la asignación de un locker para el usuario
        messages.error(request, f'{iconos["mal"]}\tDebe tener asignado un locker para utilizar este servicio.')
        return redirect('asignar_locker')
    
    return render(request, 'lavanderia.html', {'servicios':productos, 'vista':vista, 'locker':locker})

def recoger_lavanderia(request): #En este punto se hará una rutina que muestre una lista de todos los pedidos de lavanderia qué estén en estado pendiente
    pedidos = Pedido.objects.filter(area_servicio = 4, estado='pendiente')
    
    return render(request, 'recoger_lavanderia.html')

@login_required
def mantencion(request):
    return render(request, 'mantencion.html')

@login_required
def transporte(request):
    return render(request, 'transporte.html')



