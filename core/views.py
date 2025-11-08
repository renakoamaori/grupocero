from django.shortcuts import render, redirect
from .models import *
from .forms import *

# Create your views here.
def index(request):
    return render(request, 'core/index.html')
def products(request):
    return render(request, 'core/products.html')
def gallery(request):
    return render(request, 'core/gallery.html')
def about(request):
    return render(request, 'core/about.html')
def carrito(request):
    return render(request, 'core/carrito.html')
def miembros(request):
    return render(request, 'core/miembros/members.html')
def solicitud(request):
    aux = {
        'form'  : SolicitudForm()
    }
    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            form.save()  # Guardar la solicitud en la base de datos
            aux['msj'] = "¡Solicitud enviada correctamente!"
        else:
            aux['form'] = form
    return render(request, 'core/miembros/request.html', aux)