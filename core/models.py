from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _

def upload_to_artista(instance, filename):
    return f'artistas/{instance.nombre}/{filename}'

def upload_to_producto(instance, filename):
    return f'productos/{instance.artista.nombre}/{instance.titulo}/{filename}'

class Artista(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    biografia = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to=upload_to_artista, null=True, blank=True)
    sitio_web = models.URLField(null=True, blank=True)
    habilitado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class TipoProducto(models.Model):
    TIPO_CHOICES = [
        ('cancion', 'Canción'),
        ('album', 'Álbum'),
        ('ep', 'EP'),
    ]

    nom_tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nom_tipo

class Producto(models.Model):
    titulo = models.CharField(max_length=80)
    descripcion = models.TextField(null=False, blank=False)
    imagen = models.ImageField(upload_to=upload_to_producto, blank=False, null=False)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoProducto, on_delete=models.CASCADE)
    precio = models.IntegerField(default=0)
    habilitado = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo
    
class TipoUsuario(models.Model):
    TIPO_CHOICES = [
        ('comun', 'Común'),
        ('miembro', 'Miembro'),
        ('admin', 'Admin'),
    ]
    nom_tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return self.nom_tipo

class Usuario(AbstractUser):
    tipo_usuario = models.ForeignKey(TipoUsuario, on_delete=models.CASCADE)
    habilitado = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="core_usuario_groups",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="core_usuario_user_permissions",
        related_query_name="user",
    )

    def __str__(self):
        return self.username

class Solicitud(models.Model):
    ESTADO_CHOICES = [
        ('E', 'En Espera'),
        ('A', 'Aprobado'),
        ('R', 'Rechazado'),
    ]
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='E')
    nombre_producto = models.CharField(max_length=100)
    descripcion_producto = models.TextField()
    imagen_producto = models.ImageField(null=True, blank=True)
    tipo_producto = models.CharField(max_length=20, choices=TipoProducto.TIPO_CHOICES)
    precio_producto = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Solicitud #{self.pk}"

class SolicitudesRechazadas(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE)
    mensaje_rechazo = models.TextField(null=True, blank=True)