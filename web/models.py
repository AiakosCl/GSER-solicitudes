from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

# ---- Tabla de Perfiles y Usuarios ---- #
class Gerencia(models.Model):
    ceco = models.CharField(primary_key=True, max_length=5, blank=False, null=False)
    descripcion = models.CharField(max_length=70, blank=False, null=False)
    gerencia = models.CharField(max_length=50,blank=False, null=False, default="")
    aprobador = models.EmailField()

    def __str__(self) -> str:
        return f'[{self.descripcion}] - {self.ceco} - {self.aprobador}'

class AreaAccionMantencion(models.Model):
    especialidad = models.CharField(max_length=50, unique=True, null=False, blank=False)

    def __str__(self) -> str:
        return self.especialidad

class Perfiles(models.Model):
    nombre_perfil = models.CharField(max_length=10, null=False, blank=False)

    class Meta:
        verbose_name = "Perfiles"
        verbose_name_plural = "Perfiles"

    def __str__(self) -> str:
        return self.nombre_perfil

class MAE(models.Model):
    sap = models.CharField(max_length=6, primary_key=True)
    rut = models.CharField(max_length=13, blank=False, null=False, default="1-9")
    nombre=models.CharField(max_length=70, blank=False, null=False)
    sexo = models.CharField(max_length=1, null=False, blank=False, default="M")
    rol = models.CharField(max_length=10, null=True, blank=True)
    ceco_id=models.ForeignKey(Gerencia, on_delete=models.CASCADE, default='ADM01')
    cargo=models.CharField(max_length=50, null=True, blank=True)
    jornada = models.CharField(max_length=10, null=False, blank=True)
    grupo = models.CharField(max_length=10, null=True, blank= True)
    telefono = models.CharField(max_length=12, null=True, blank=True)
    correo = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        verbose_name = "MAE"
        verbose_name_plural = "MAE"
    def __str__(self) -> str:
        return f'[{self.ceco_id}] - {self.nombre} - {self.cargo}'

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    rut = models.CharField(max_length=10, unique=True)
    ceco_id = models.ForeignKey(Gerencia, on_delete=models.CASCADE, default="ADM01")
    telefono = models.CharField(max_length=20)
    tipo_usuario = models.ForeignKey(Perfiles, on_delete=models.CASCADE, default=3)
    lavanderia = models.BooleanField(default=True)
    alimentacion = models.BooleanField(default=False)
    hoteleria = models.BooleanField(default=False)
    transporte = models.BooleanField(default=False)
    mantencion = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
    def __str__(self):
        return f'[{self.username}] - {self.last_name}, {self.first_name} {self.email}'

class Tecnico(models.Model):
    rut = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=70, blank=False, null=False)
    telefono = models.CharField(max_length=12, null=True, blank=True)
    correo = models.CharField(max_length=50, blank=False, null=False)
    especialidad = models.ForeignKey(AreaAccionMantencion, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tecnico"
        verbose_name_plural = "Tecnicos"

    def __str__(self) -> str:
        return f'[{self.rut}] - {self.nombre} - {self.especialidad}'

# --- Tablas de Edificios y Oficinas --- #
class Area(models.Model):
    nombre_area=models.CharField(max_length=20, null=False, blank=False)

    def __str__(self) -> str:
        return self.nombre_area

class Edificio(models.Model):
    TIPO_EDIFICIO = (
        ('Hotel', 'Hotel'), 
        ('Mina_Rajo', 'Mina_Rajo'),
        ('Taller', 'Taller'),
        ('Otros', 'Otros'))
    nombre_edificio = models.CharField(max_length=50, unique=True, null=False, blank=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    tipo_edificio = models.CharField(max_length=10, choices=TIPO_EDIFICIO, null=False, blank=False)

    def __str__(self):
        return f'[{self.nombre_edificio}] - Area: {self.area}'
    
class Habitacion(models.Model):
    nombre_habitacion = models.CharField(max_length=50, unique=True, null=False, blank=False)
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE)

    def __str__(self):
        return f'[{self.nombre_habitacion}] - Edificio: {self.edificio}'
    
    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"

class SalasCambio(models.Model):
    nombre_sala = models.CharField(max_length=50, unique=True, null=False, blank=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return f'[{self.nombre_sala}] - Area: {self.area}'
    
class Lockers(models.Model):
    LUGAR_TRABAJO= (
        ('Saladillo', 'Saladillo'),
        ('SPMFC', 'SPMFC'),
        ('Nivel_16', 'Nivel_16'),
        ('Nivel_19', 'Nivel_19'),
        ('Concentradora', 'Concentradora'),
        ('Mina_Rajo', 'Mina_Rajo'),
    )
    numero_locker = models.PositiveIntegerField(null=False, blank=False)
    nombre_locker = models.CharField(max_length=5, null=False, blank=False)
    usuario_locker = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    lugar_trabajo = models.CharField(max_length=20, choices=LUGAR_TRABAJO, null=False, blank=False)
    casacambio= models.ForeignKey(SalasCambio, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "Locker"
        verbose_name_plural = "Lockers"
    
    def __str__(self):
        return f'[{self.nombre_locker}] - Casa de Cambio: {self.casacambio} - Usuario: {self.usuario_locker}'
    
    def save(self, *args, **kwargs):
        # Generar el nombre del locker a partir del nombre de la sala de cambio y el número de locker
        if not self.nombre_locker:  # Si el nombre no ha sido asignado manualmente
            self.nombre_locker = f'{self.casacambio.nombre_sala[:2].upper()}-{self.numero_locker}'
        
        super().save(*args, **kwargs)


# --- Tabla de Servicios --- #

class AreaServicio(models.Model):
    nombre_area = models.CharField(max_length=50, unique=True, blank=False, null=False)
    imagen = models.ImageField(upload_to='servicios', null=True, blank=True)
    descripcion = models.TextField(blank=False, null=False, default="Sin info")
    administrador = models.EmailField(blank=False, null=False)

    class Meta:
        verbose_name = "Area de Servicio"
        verbose_name_plural = "Areas de Servicio"

    def __str__(self):
        return f'[{self.nombre_area}] - Administrador: {self.administrador}'

class Servicio(models.Model):
    nombre_servicio = models.CharField(max_length=50, unique=True, null=False, blank=False)
    descripcion_servicio = models.TextField(blank=False)
    area_servicio = models.ForeignKey(AreaServicio, on_delete=models.CASCADE)
    precio_servicio = models.PositiveBigIntegerField(default=0)
    imagen = models.ImageField(upload_to='servicios', null=True, blank=True)
    autorizacion = models.BooleanField(default=False, blank=False, null=False)
    aprobador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'tipo_usuario': 2})  # Solo los aprobadores pueden aparecer aquí

    class Meta:
        verbose_name = "Servicios"
        verbose_name_plural = "Servicios"
    def __str__(self):
        return f'[{self.nombre_servicio}] - {self.area_servicio} - {self.autorizacion}'

class TareasMantencion(models.Model):
    nombre_tarea = models.CharField(max_length=50, unique=True, null=False, blank=False)
    area_accion = models.ForeignKey(AreaAccionMantencion, on_delete=models.CASCADE)
    descripcion_tarea = models.TextField(blank=False)
    timing = models.PositiveBigIntegerField(default=0)

class Valoracion(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id= models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
        )  # Generará una validación de 1 a 5
    comentario = models.TextField(blank=True, null=True)
    fecha_valoracion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"

    def __str__(self):
        return f'Valoración de {self.usuario.username} para la Solicitud #{self.solicitud.id}'


# ---- Trabajo con Contacto ---- #
class Contactos(models.Model):
    ContactoId = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    NombreCliente= models.CharField(max_length=64, blank=False, null=True)
    EmailCliente = models.EmailField(max_length=50, blank=False, null=True)
    Mensaje = models.TextField(blank=False)

    def __str__(self) -> str:
        return self.NombreCliente


# ---- Trabajo Solicitudes, carritos y otros ---- #

class SolicitudBase(models.Model): #Para Registro de Solicitudes de sobrecupo mantención camionetas
    ESTADO_SOLICITUD = (
    ('pendiente', 'Pendiente'),
    ('aprobada', 'Aprobada'),
    ('rechazada', 'Rechazada'),
    ('completada', 'Completada')
)
    id = models.CharField(max_length=20, primary_key=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    area_servicio = models.ForeignKey(AreaServicio, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    estado = models.CharField(max_length=15, choices=ESTADO_SOLICITUD, default='pendiente')

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.id:
            area_abreviado = self.area_servicio.nombre_area[0:3].upper()
            anio_actual = timezone.now().year
            total_solicitudes = Sobrecupo.objects.all().count() + 1
            correlativo = f'{total_solicitudes:04d}'
            self.id = f'{self.area_servicio.id}-{area_abreviado}-{anio_actual}-{correlativo}'
        super().save(*args, **kwargs)

class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Carrito de: {self.usuario.username}'

class ItemsCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.cantidad} x {self.producto.nombre_servicio}'

class Pedido(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f'Pedido #{self.id} - Usuario: {self.usuario.username}'

class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, default = 0)

    def __str__(self) -> str:
        return f'{self.cantidad} x {self.producto.nombre_servicio}'

class OT(SolicitudBase): #Para registro de OT Mantención
    tecnico_asignado = models.ForeignKey(Tecnico, on_delete=models.CASCADE, limit_choices_to={'estado': True})
    tarea_mantencion = models.ForeignKey(TareasMantencion, on_delete=models.CASCADE)
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, limit_choices_to={'edificio': edificio})
    imagen_ot = models.ImageField(upload_to='ot', null=True, blank=True) #Permitirá tomar una foto en cuestión y subirla, aunque no será obligatorio.
    imagen_cierre = models.ImageField(upload_to='ot', null=True, blank=True) #Subir evidencia de lo que se realizó.
    comentario = models.TextField(blank=True, null=True)
    
    class meta:
        verbose_name = "OT Correctiva"
        verbose_name_plural = "OTs Correctivas"
    
    def __str__(self) -> str:
        return f'OT {self.id} - {self.edificio} - {self.habitacion} - {self.tarea_mantencion} - {self.tecnico_asignado.nombre}'


class Alojamiento(SolicitudBase): #Para registro de Solicitud de Alojamiento
    pass

class Movilizacion(SolicitudBase): #Para registro de Solicitud de Transporte
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    pass

class Sobrecupo(SolicitudBase): #Para Registro de Solicitudes de sobrecupo mantención camionetas
    MOTIVO_SOBRECUPO = (
        ('mantenimiento', 'Mantenimiento'),
        ('revisión técnica', 'Revisión Técnica'),
        ('limpieza', 'Limpieza'),
        ('fuera de servicio', 'Fuera de Servicio'),
    )
    patente = models.CharField(max_length=10)
    nro_interno = models.CharField(max_length=10)
    fecha_sobrecupo = models.DateTimeField(auto_now_add=True)
    kilometraje = models.PositiveBigIntegerField(default=0)
    motivo = models.CharField(max_length=25, choices=MOTIVO_SOBRECUPO, default='mantenimiento')

    def __str__(self) -> str:
        return f'Solicitud de: {self.usuario.username} - ID: #{self.id}'