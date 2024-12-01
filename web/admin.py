from django.contrib import admin
from .models import *

# Personalización de las visualizaciones

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')

class GerenciaAdmin(admin.ModelAdmin):
    list_display = ('ceco', 'descripcion', 'gerencia', 'aprobador')
    list_filter = ('ceco', 'descripcion', 'gerencia', 'aprobador')
    search_fields = ('ceco', 'descripcion', 'gerencia', 'aprobador')

class AreaAdmin(admin.ModelAdmin):
    list_display = ('id','nombre_area', )
    list_filter = ('nombre_area', )
    search_fields = ('nombre_area', )

class AreaServicioAdmin(admin.ModelAdmin):
    list_display = ('id','nombre_area', 'administrador')
    list_filter = ('nombre_area', 'administrador')
    search_fields = ('nombre_area', 'administrador')

class ServicioAdmin(admin.ModelAdmin):
    list_display = ('id','nombre_servicio','area_servicio' )
    list_filter = ('nombre_servicio','area_servicio' )
    search_fields = ('nombre_servicio','area_servicio')

class ContactoAdmin(admin.ModelAdmin):
    list_display = ('ContactoId','usuario','tipo_contacto','area','emailcliente','telefono','mensaje' )
    list_filter = ('usuario','tipo_contacto','area','emailcliente','telefono','mensaje' )
    search_fields = ('usuario','tipo_contacto','area','emailcliente','telefono','mensaje' )

class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'area_servicio')

class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'area_servicio','usuario','estado')

class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'pedido')
    list_filter = ('pedido',)

class IconosBase64Admin(admin.ModelAdmin):
    list_display = ('id', 'icono')
    list_filter = ('icono',)


# Modelos que aparecerán en la consola de admin
admin.site.register(MAE)
admin.site.register(Usuario, UserAdmin)
admin.site.register(Area, AreaAdmin)
admin.site.register(Edificio)
admin.site.register(Habitacion)
admin.site.register(Gerencia, GerenciaAdmin)
admin.site.register(Perfiles)
admin.site.register(Lockers)
admin.site.register(Servicio, ServicioAdmin)
admin.site.register(AreaServicio, AreaServicioAdmin)
admin.site.register(SalasCambio)
admin.site.register(Contacto, ContactoAdmin)
admin.site.register(Carrito, CarritoAdmin)
admin.site.register(Pedido, PedidoAdmin)
admin.site.register(DetallePedido, DetallePedidoAdmin)
admin.site.register(ItemsCarrito)
admin.site.register(ContadorSolicitudes)
admin.site.register(IconosBase64, IconosBase64Admin)
