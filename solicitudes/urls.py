"""
URL configuration for solicitudes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from web.views import *


urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', index, name='inicio'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('registro/', nuevo_usuario, name='NuevoUsuario'),
    path('editar-usuario/<int:usuario_id>/', editar_usuario, name='EditarUsuario'),
    path('eliminar-usuario/<int:usuario_id>/', eliminar_usuario, name='EliminarUsuario'),
    path('ficha/<int:usuario_id>/', vista_ficha, name='Ficha'),
    path('usuarios/', lista_usuarios, name="ListaUsuarios" ),
    path('filtrousuarios/', filtrarUsuarios, name='FiltroUsuarios'),
    path('filtro/', filtrar_articulos, name='buscar_articulo'),
    path('solicitudes_lavanderia/', ver_solicitudes_lavanderia, name='ver_solicitudes_lavanderia'),
    path('ticket_lavanderia/', ticket_lavanderia, name='ticket_lavanderia'),
    path('locker_usuario/', asignar_locker, name='asignar_locker'),
    path('servicios_disponibles/<int:area_servicio>/', lista_servicios, name='lista_servicios'),
    path('carrito/agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', ver_carrito, name='ver_carrito'),
    path('pedido/', realizar_pedido, name='realizar_pedido'),
    path('carrito/vaciar/', vaciar_carrito, name='vaciar_carrito'),
    path('carrito/eliminar/<int:elemento_id>/', eliminar_item_carrito, name='eliminar_linea'),
    path('carrito/aumentar/<int:elemento_id>/', aumentar_item, name='aumentar_item'),
    path('carrito/disminuir/<int:elemento_id>/', disminuir_item, name='disminuir_item'),
    path('historial-pedidos/', historial, name='historial'),
    path('contacto/', contacto, name='contacto'),
    path('servicios/<int:id_areaservicio>/', solicitar, name='solicitar'),
    path('servicios/alimentacion/', alimentacion, name='alimentacion'),
    path('servicios/hoteleria/', hoteleria, name='hoteleria'),
    path('servicios/mantencion/', mantencion, name='mantencion'),
    path('servicios/lavanderia/', lavanderia, name='lavanderia'),
    path('servicios/transporte/', transporte, name='transporte'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
