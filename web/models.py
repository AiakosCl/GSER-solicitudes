from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

# Create your models here.
class Gerencia(models.Model):
    ceco = models.CharField(primary_key=True, max_length=5, blank=False, null=False)
    descripcion = models.CharField(max_length=70, blank=False, null=False)
    gerencia = models.CharField(max_length=50,blank=False, null=False, default="")
    aprobador = models.EmailField()

    def __str__(self) -> str:
        return f'[{self.descripcion}] - {self.ceco} - {self.aprobador}'

class Perfiles(models.Model):
    nombre_perfil = models.CharField(max_length=10, null=False, blank=False)

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

    def __str__(self):
        return f'[{self.username}] - {self.last_name}, {self.first_name} {self.email}'
    
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

class AreaServicio(models.Model):
    nombre_area = models.CharField(max_length=50, unique=True, blank=False, null=False)
    imagen = models.ImageField(upload_to='servicios', null=True, blank=True)
    administrador = models.EmailField(blank=False, null=False)


    def __str__(self):
        return f'[{self.nombre_area}] - Administrador: {self.administrador}'
    
class Servicios(models.Model):
    nombre_servicio = models.CharField(max_length=50, unique=True, null=False, blank=False)
    descripcion_servicio = models.TextField(blank=False)
    area_servicio = models.ForeignKey(AreaServicio, on_delete=models.CASCADE)
    precio_servicio = models.PositiveBigIntegerField(default=0)
    imagen = models.ImageField(upload_to='servicios', null=True, blank=True)
    autorizacion = models.BooleanField(default=False, blank=False, null=False)
    aprobador = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'tipo_usuario': 2})  # Solo los aprobadores pueden aparecer aquí

    def __str__(self):
        return f'[{self.nombre_servicio}] - {self.area_servicio} - {self.autorizacion}'
    
class Solicitud(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ESTADO_SOLCITID = (
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('completada', 'Completada')
        )
    estado = models.CharField(max_length=15, choices=ESTADO_SOLCITID, default='pendiente')
    fecha_completada = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f'Solicitud de: {self.usuario.last_name}, {self.usuario.first_name} - Estado: {self.estado}'
    
    class Meta:
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"

class ItemsSolicitud(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    fecha_servicio = models.DateField(auto_now_add=True)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.cantidad} x {self.servicio.nombre_servicio}'

class HistoricoSolicitud(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, null=True, blank=True)
    fecha_evento = models.DateTimeField(auto_now_add=True)
    descripcion_evento = models.TextField()
    estado_solicitud = models.CharField(max_length=15)

    def __str__(self) -> str:
        return f'Solicitud #{self.id} - Usuario: {self.usuario.username}'

class DetalleHistorico(models.Model):
    historico = models.ForeignKey(HistoricoSolicitud, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=0, default = 0)

    def __str__(self) -> str:
        return f'{self.cantidad} x {self.servicio.nombre_servicio}'

class Valoracion(models.Model):
    solicitud = models.OneToOneField(Solicitud, on_delete=models.CASCADE)  # Solo puede valorarse una vez por solicitud
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

    def __str__(self):
        return f'[{self.nombre_locker}] - Casa de Cambio: {self.casacambio} - Usuario: {self.usuario_locker}'
    def save(self, *args, **kwargs):
        # Generar el nombre del locker a partir del nombre de la sala de cambio y el número de locker
        if not self.nombre_locker:  # Si el nombre no ha sido asignado manualmente
            self.nombre_locker = f'{self.casacambio.nombre_sala[:2].upper()}-{self.numero_locker}'
        
        super().save(*args, **kwargs)

