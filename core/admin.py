from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Artista)
admin.site.register(TipoProducto)
admin.site.register(TipoUsuario)
admin.site.register(Producto)
admin.site.register(Usuario)
admin.site.register(Solicitud)
admin.site.register(SolicitudesRechazadas)