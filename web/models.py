from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


# ---- Otros ----  #

class IconosBase64(models.Model):
    icono = models.CharField(max_length=100, null=False, blank=False)
    icono_base64 = models.TextField(null=False, blank=False)

    def __str__(self) -> str:
        return self.icono

# ---- Tabla de Perfiles y Usuarios ---- #


class Gerencia(models.Model): #Maesto de Gerencias y Centros de Costos
    ceco = models.CharField(primary_key=True, max_length=5, blank=False, null=False)
    descripcion = models.CharField(max_length=70, blank=False, null=False)
    gerencia = models.CharField(max_length=50,blank=False, null=False, default="")
    aprobador = models.EmailField()

    def __str__(self) -> str:
        return f'[{self.ceco}] - {self.descripcion}'

class Especialidad(models.Model): #Maestro de especialidades de mantención (Electricidad, Plomería, etc.)
    especialidad = models.CharField(max_length=50, unique=True, null=False, blank=False)

    def __str__(self) -> str:
        return self.especialidad

class Perfiles(models.Model): #Perfiles de los usuarios, acá podrá especificarse su acceso también.
    nombre_perfil = models.CharField(max_length=10, null=False, blank=False)

    class Meta:
        verbose_name = "Perfiles"
        verbose_name_plural = "Perfiles"

    def __str__(self) -> str:
        return self.nombre_perfil

class MAE(models.Model): #Maestro de Personal de dónde se obtendrán los datos para crear el Usuario.
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

class Usuario(AbstractUser): #Maestro de usuarios, que obtendrá la información desde un Maestro de Personal.
    GENERO = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )

    email = models.EmailField(unique=True)
    rut = models.CharField(max_length=10, unique=True)
    ceco_id = models.ForeignKey(Gerencia, on_delete=models.CASCADE, default="ADM01")
    telefono = models.CharField(max_length=20)
    genero = models.CharField(max_length=1, choices=GENERO, null=True, blank=True, default="M")
    tipo_usuario = models.ForeignKey(Perfiles, on_delete=models.CASCADE, default=3)
    servicio_autorizado = models.ManyToManyField('AreaServicio', blank=True)
    
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
    def __str__(self):
        return f'{self.last_name}, {self.first_name} | {self.email}'

class Tecnico(models.Model): #Mantenedor de Tecnicos por su especialidad para la asignación de tareas de mantención levantadas por el sistema.
    rut = models.CharField(max_length=10, primary_key=True)
    nombre = models.CharField(max_length=70, blank=False, null=False)
    telefono = models.CharField(max_length=12, null=True, blank=True)
    correo = models.CharField(max_length=50, blank=False, null=False)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tecnico"
        verbose_name_plural = "Tecnicos"

    def __str__(self) -> str:
        return f'[{self.rut}] - {self.nombre} - {self.especialidad}'


# --- Tablas de Edificios y Oficinas --- #


class Area(models.Model): #Mantenedor de áreas en dónde se encuentran los edificios de la división.
    nombre_area=models.CharField(max_length=20, null=False, blank=False)

    def __str__(self) -> str:
        return self.nombre_area

class Edificio(models.Model): #Mantenedor de edificios existentes en la División, y que tendrán habitaciones en dónde actuar.
    TIPO_EDIFICIO = (
        ('Hotel', 'Hotel'), 
        ('nodo 3500', 'Nodo 3500'),
        ('nodo 3700', 'Nodo 3700'),
        ('Taller', 'Taller'),
        ('Otros', 'Otros'))
    nombre_edificio = models.CharField(max_length=50, unique=True, null=False, blank=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    tipo_edificio = models.CharField(max_length=10, choices=TIPO_EDIFICIO, null=False, blank=False)

    def __str__(self):
        return f'[{self.nombre_edificio}] - Area: {self.area}'
    
class Habitacion(models.Model): #Mantenedor de habitaciones existentes, y se refiere a tipo, como por ejemplo dormitorios, oficinas, baños, etc.
    TIPO_HABITACION = (
        ("dormitorio", "Dormitorio"),
        ("comedor", "Comedor"),
        ("oficina", "Oficina"),
        ("baño", "Baño"),
        ("sala de cambio", "Sala de Cambio"),
        ("sala de reuniones", "Sala de Reuniones"),
        ("otro", "Otro"),
    )
    edificio = models.ForeignKey(Edificio, on_delete=models.CASCADE)
    nombre_habitacion = models.CharField(max_length=50, unique=True, null=False, blank=False)
    tipo_habitacion = models.CharField(max_length=50, choices=TIPO_HABITACION, null=False, blank=False, default="dormitorio")


    def __str__(self):
        return f'[{self.nombre_habitacion}] - Edificio: {self.edificio}'
    
    class Meta:
        verbose_name = "Habitación"
        verbose_name_plural = "Habitaciones"

class SalasCambio(models.Model): #Mantenedor de Casa de Cambios existentes
    nombre_sala = models.CharField(max_length=50, unique=True, null=False, blank=False)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def __str__(self):
        return f'[{self.nombre_sala}] - Area: {self.area}'
    
class Lockers(models.Model): #Mantenedor de Lockers a asignar al usuario.
    SEXO = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    )
    numero_locker = models.PositiveIntegerField(null=False, blank=False)
    nombre_locker = models.CharField(max_length=5, null=True, blank=True)
    usuario_locker = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    genero = models.CharField(max_length=1, choices=SEXO, null=True, blank=True)
    lugar_trabajo = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    casacambio= models.ForeignKey(SalasCambio, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        verbose_name = "Locker"
        verbose_name_plural = "Lockers"
    
    def __str__(self):
        return self.nombre_locker
    
    def save(self, *args, **kwargs):
        # Generar el nombre del locker a partir del nombre de la sala de cambio y el número de locker
        if not self.nombre_locker:  # Si el nombre no ha sido asignado manualmente
            self.nombre_locker = f'{self.casacambio.nombre_sala[:3].upper()}-{self.numero_locker}'
        
        super().save(*args, **kwargs)


# --- Tabla de Servicios --- #


class AreaServicio(models.Model): #Mantenedor de áreas de servicios (Alimentación, hotelería, mantención, etc.)
    nombre_area = models.CharField(max_length=50, unique=True, blank=False, null=False)
    imagen = models.ImageField(upload_to='servicios', null=True, blank=True)
    descripcion = models.TextField(blank=False, null=False, default="Sin info")
    administrador = models.EmailField(blank=False, null=False)
    vista = models.CharField(max_length=50, default='mantencion', blank=False, null=False)
    icono = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Area de Servicio"
        verbose_name_plural = "Areas de Servicio"

    def __str__(self):
        return self.nombre_area

class Servicio(models.Model): #Acá se registrarán todos los servicios con detalle multilínea, como por ejemplo: Servicios de alimentación o lavandería, en dónde en una solicitud se puede especificar más de un servicio en una única solicitud.
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

class TareasMantencion(models.Model): #Tareas de Mantenimiento (mantenedores)
    nombre_tarea = models.CharField(max_length=50, unique=True, null=False, blank=False)
    area_accion = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    descripcion_tarea = models.TextField(blank=False)
    timing = models.PositiveBigIntegerField(default=0)

class Valoracion(models.Model): #Acá se guardará la valorización de los servicios una vez finalizados para registro y métricas de satisfacción.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=1)
    object_id= models.PositiveIntegerField(default=1)
    content_object = GenericForeignKey('content_type', 'object_id')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
        )  # Generará una validación de 1 a 5
    comentario = models.TextField(blank=True, null=True, default="Sin comentarios")
    fecha_valoracion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"

    def __str__(self):
        return f'Valoración de {self.usuario.username} para la Solicitud #{self.solicitud.id}'


# ---- Trabajo con Contacto / reclamo / sugerencias, etc ---- #


class Contacto(models.Model): # Tabla de contacto a la superintendencia, para registro de reclamos, sugerencias, felicitaciones, etc.
    TIPO_CONTACTO = (
        ('consulta', 'Consulta'),
        ('felicitacion', 'Felicitación'),
        ('sugerencia', 'Sugerencia'),
        ('reclamo', 'Reclamo'),
        ('otro', 'Otro'),
    )
    ContactoId = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipo_contacto = models.CharField(max_length=20, choices=TIPO_CONTACTO, null=False, blank=False)
    area = models.ForeignKey(AreaServicio, on_delete=models.CASCADE, default=1)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    emailcliente = models.EmailField(max_length=50, blank=False, null=False)
    telefono = models.CharField(max_length=10, null=True, blank=True)
    mensaje = models.TextField(null=False, blank=False)

    def __str__(self) -> str:
        return f"{self.fecha_creacion.strftime('%d-%m-%Y %H:%M')} - {self.get_tipo_contacto_display()} - {self.emailcliente} - {self.area.nombre_area}"


# ---- Trabajo Solicitudes, carritos y otros ---- #


class ContadorSolicitudes(models.Model): # Contador de Solicitudes. Acá se obtendrá el número de registro de cada tipo de servicio para generar el contador.
    total_solicitudes = models.PositiveIntegerField(default=0)

    @classmethod
    def incrementar(cls):
        contador, created = cls.objects.get_or_create(pk=1)
        contador.total_solicitudes += 1
        contador.save()
        return contador.total_solicitudes

class SolicitudBase(models.Model): #Para Registro de Solicitudes de sobrecupo mantención camionetas
    ESTADO_SOLICITUD = (
    ('pendiente', 'Pendiente'),
    ('aprobada', 'Aprobada'),
    ('en proceso', 'En Proceso'),
    ('rechazada', 'Rechazada'),
    ('completada', 'Completada')
)
    id = models.CharField(max_length=20, primary_key=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    area_servicio = models.ForeignKey(AreaServicio, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    ceco = models.ForeignKey(Gerencia, on_delete=models.CASCADE)
    estado = models.CharField(max_length=15, choices=ESTADO_SOLICITUD, default='pendiente')

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if not self.id:
            area_abreviado = self.area_servicio.nombre_area[0:3].upper()
            anio_actual = timezone.now().year
            correlativo = ContadorSolicitudes.incrementar() # Obtiene el el correlativo de las solicitudes
            self.id = f'{self.area_servicio.id}-{area_abreviado}-{anio_actual}-{correlativo:04d}'
        super().save(*args, **kwargs)

class Carrito(models.Model): #Este carrito llevará el pedido de servicios que puedan ser multiples, como por ejemplo Servicios de Alimentación y/o la Lavendería.
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    area_servicio = models.ForeignKey(AreaServicio, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Carrito de: {self.usuario.username}'

class ItemsCarrito(models.Model): #Acá se llevará el registro de cada artículo de algún pedido multilínea.
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE)
    producto = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.cantidad} x {self.producto.nombre_servicio}'

class Pedido(SolicitudBase): #Acá se registrará el pedido multilínea y el total de los mismos. Por ejemplo, Servicios de Alimentación y/o la Lavendería.
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.id

class DetallePedido(models.Model): #El pedido multilínea se registrará en el detalle del pedido.
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
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    imagen_ot = models.ImageField(upload_to='ot', null=True, blank=True) #Permitirá tomar una foto en cuestión y subirla, aunque no será obligatorio.
    imagen_cierre = models.ImageField(upload_to='ot', null=True, blank=True) #Subir evidencia de lo que se realizó.
    comentario = models.TextField(blank=True, null=True)
    
    class meta:
        verbose_name = "OT Correctiva"
        verbose_name_plural = "OTs Correctivas"
    
    def __str__(self) -> str:
        return f'OT {self.id} - {self.edificio} - {self.habitacion} - {self.tarea_mantencion} - {self.tecnico_asignado.nombre}'

class Alojamiento(SolicitudBase): #Para registro de Solicitud de Alojamiento
    MOTIVOS_ALOJAMIENTO = (
        ('parada de planta', 'Parada de Planta'),
        ('encierro', 'Encierro Programado'),
        ('contingencias', 'Contingencias'),
        ('permanente', 'Permanente'),
        ('Alojamiento por contrato', 'Alojamiento por Contrato'),
        ('visita', 'Visita'),
    )
    
    check_in = models.DateField()
    check_out = models.DateField()
    tipo_alojamiento = models.CharField(max_length=30, choices=MOTIVOS_ALOJAMIENTO, default='visita')
    cantidad = models.PositiveIntegerField(default=1)
    listado = models.FileField(upload_to='alojamientos', null=False, blank=False) #Deberá ingresarse el Excel con la lista de personas para la solicitud.
    comentario = models.TextField(blank=True, null=True)

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
