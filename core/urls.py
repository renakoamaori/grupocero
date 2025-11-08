from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name="index"),
    path('productos', products, name="productos"),
    path('galeria', gallery, name="galeria"),
    path('acerca', about, name="acerca"),
    path('carrito', carrito, name="carrito"),
    path('miembros', miembros, name="miebros"),
    path('solicitud', solicitud, name="solicitud"),
]