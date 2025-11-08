import asyncio
import shutil
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login
from .models import *
from .forms import *
import os
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from PIL import Image, ImageOps
import re
from django.conf import settings

def create_horizontal_image(input_image_path, output_image_path, target_width=1800, target_height=400):
    try:
        # Load input image
        im = Image.open(input_image_path)

        # If the image is RGBA, convert it to RGB
        if im.mode == 'RGBA':
            im = im.convert('RGB')

        # Resize input image while keeping aspect ratio
        ratio = target_height / im.height
        im_resized = im.resize((int(im.width * ratio), target_height))

        # Border parameters
        fill_color = (255, 255, 255)
        border_l = int((target_width - im_resized.width) / 2)

        # Use ImageOps.expand()
        border_r = target_width - im_resized.width - border_l
        im_horizontal = ImageOps.expand(im_resized, (border_l, 0, border_r, 0), fill_color)
        im_horizontal.save(output_image_path)
    except Exception as e:
        print(f"Error al crear la imagen horizontal: {e}")

def procesar_imagen(imagen, este_artista):
    try:
        nombre_limpio = re.sub(r'\W+', '', este_artista.nombre, flags=re.UNICODE)
        output_image_path = os.path.join(settings.MEDIA_ROOT, 'artistas', nombre_limpio, f'{nombre_limpio}_h.jpg')
        if not os.path.exists(output_image_path):
            create_horizontal_image(imagen.path, output_image_path)

        # Genera la ruta relativa
        imagen_banner = settings.MEDIA_URL + os.path.relpath(output_image_path, start=settings.MEDIA_ROOT)

        return imagen_banner
    except Exception as e:
        print(f"Error al procesar la imagen: {e}")
        return None

def obtener_imagen(lista):
    if lista and lista[0].imagen:
        return lista[0].imagen
    return None

def procesar_listas(s, a, e, este_artista):
    for lista in [s, a, e]:
        imagen = obtener_imagen(lista)
        if imagen:
            return procesar_imagen(imagen, este_artista)

    # Si ninguna de las listas tiene una imagen, procesar la imagen del artista
    return procesar_imagen(este_artista.imagen, este_artista)

def get_artistaysusproductoshabilitados(artista_id):
    aux = {}
    try:
        este_artista = Artista.objects.get(pk=artista_id)
        aux['este_artista'] = este_artista
    except Artista.DoesNotExist:
        return aux

    try:
        tipo1 = TipoProducto.objects.get(nom_tipo='cancion')
        s = Producto.objects.filter(habilitado=True, tipo=tipo1, artista=este_artista)
        aux['productos_sencillos'] = s
    except TipoProducto.DoesNotExist:
        pass

    try:
        tipo2 = TipoProducto.objects.get(nom_tipo='album')
        a = Producto.objects.filter(habilitado=True, tipo=tipo2, artista=este_artista)
        aux['productos_albums'] = a
    except TipoProducto.DoesNotExist:
        pass

    try:
        tipo3 = TipoProducto.objects.get(nom_tipo='ep')
        e = Producto.objects.filter(habilitado=True, tipo=tipo3, artista=este_artista)
        aux['productos_eps'] = e
    except TipoProducto.DoesNotExist:
        pass

    if 'productos_sencillos' in aux or 'productos_albums' in aux or 'productos_eps' in aux:
        imagen_banner = procesar_listas(s, a, e, este_artista)
        aux['imagen_banner'] = imagen_banner

    return aux

def get_artistasyproductoshabilitados():
    aux = {}
    try:
        tipo1 = TipoProducto.objects.get(nom_tipo='cancion')
        aux['productos_sencillos'] = Producto.objects.filter(habilitado=True, tipo=tipo1).order_by('pk')
    except TipoProducto.DoesNotExist:
        pass

    try:
        tipo2 = TipoProducto.objects.get(nom_tipo='album')
        aux['productos_albums'] = Producto.objects.filter(habilitado=True, tipo=tipo2).order_by('pk')
    except TipoProducto.DoesNotExist:
        pass

    try:
        tipo3 = TipoProducto.objects.get(nom_tipo='ep')
        aux['productos_eps'] = Producto.objects.filter(habilitado=True, tipo=tipo3).order_by('pk')
    except TipoProducto.DoesNotExist:
        pass

    if Artista.objects.filter(habilitado=True).exists():
        aux['artistas'] = Artista.objects.filter(habilitado=True).order_by('pk')

    return aux

def get_info_modals():

    modal_mimori = get_object_or_404(Producto, pk=11)
    modal_akari = get_object_or_404(Producto, pk=18)
    modal_tomori = get_object_or_404(Producto, pk=17)

    return {
        'modal_mimori': modal_mimori,
        'modal_akari': modal_akari,
        'modal_tomori': modal_tomori
    }
#VISTAS GENERALES:
def index(request):
    try:
        aux = get_artistasyproductoshabilitados()
        aux2 = get_info_modals()
        
        # Combinar los diccionarios
        context = {**aux, **aux2}
    except:
        context = None

    return render(request, 'core/index.html', context)
def register(request):
    aux = {
        'form': registerForm()
    }
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            tipo = get_object_or_404(TipoUsuario, nom_tipo='comun')
            user = form.save(commit=False)
            user.tipo_usuario = tipo
            user.save()
            group, created = Group.objects.get_or_create(name='comun')
            user.groups.add(group)
            user.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('index')
        else:
            aux['form'] = form
    return render(request, 'registration/register.html', aux)
def products(request):
    try:
        aux = get_artistasyproductoshabilitados()
    except:
        aux = None
    return render(request, 'core/products.html', aux)
def gallery(request):
    productos_list = Producto.objects.filter(habilitado=True).order_by('pk')
    paginator = Paginator(productos_list, 6) # Muestra 6 productos por página

    page_number = request.GET.get('page')
    productos_all = paginator.get_page(page_number)
    aux = {
        'productos_all': productos_all
    }
    return render(request, 'core/gallery.html', aux)
def about(request):
    return render(request, 'core/about.html')
def carrito(request):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        aux = {
            'carrito': Carrito.objects.filter(usuario=request.user)
        }
    else:
        messages.error(request, '¡Por favor inicie sesión para comenzar a agregar productos al carrito!')
        aux = None
    return render(request, 'core/carrito.html', aux)
def agregar_producto_carrito(request, producto_id):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        producto = get_object_or_404(Producto, pk=producto_id)
        if Carrito.objects.filter(usuario=request.user, producto=producto):
            messages.error(request, '¡El producto ya está en el carrito!')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            c = Carrito(
                usuario = request.user, 
                producto = producto
                )
            c.save()
            messages.success(request, '¡Producto agregado correctamente!')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        messages.error(request, '¡Debe haber iniciado sesión para agregar el producto al carrito!')
    return redirect(request.META.get('HTTP_REFERER'))
def eliminar_producto_carrito(request, producto_id):
    messages.get_messages(request).used = True
    if request.user.is_authenticated:
        producto = get_object_or_404(Producto, pk=producto_id)
        item = Carrito.objects.filter(usuario=request.user, producto=producto)
        if item:
            item.delete()
        else:
            messages.error(request, '¡El producto no existe en el carrito!')
            return redirect('carrito')
    else:
        return redirect(request.META.get('HTTP_REFERER'))
    return redirect('carrito')
def cantidad_productos_carrito(request):
    if request.user.is_authenticated:
        try:
            contador = Carrito.objects.filter(usuario=request.user).count()
        except Exception as e:
            print(e)
            contador = 0
    else:
        contador = 0
    return contador
def artista(request, artista_id):
    try:
        aux = get_artistaysusproductoshabilitados(artista_id)
    except:
        aux = None
    return render(request, 'core/artista.html', aux)
#VISTAS DE MIEMBROS
def miembros(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario == 'comun':
            return redirect('')
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
        solicitudA = SolicitudA.objects.filter(usuario=request.user)
        solicitudP = SolicitudP.objects.filter(usuario=request.user)
        solicitudesArechazadas = SolicitudesRechazadas.objects.filter(solicitudA__in=solicitudA)
        solicitudesPrechazadas = SolicitudesRechazadas.objects.filter(solicitudP__in=solicitudP)
        aux = {
            'listaA' : solicitudA,
            'listaP' : solicitudP,
            'listaRA' : solicitudesArechazadas,
            'listaRP' : solicitudesPrechazadas
        }
        return render(request, 'core/miembros/members.html', aux)
    else:
        return redirect('')
def solicitudP(request):
    aux = {'form': SolicitudPForm()}
    
    if request.method == 'POST':
        form = SolicitudPForm(request.POST, request.FILES)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.imagen_producto = None  # Asegúrate de que la imagen no se guarde en este punto
            solicitud.save()  # Guarda la instancia primero para obtener un ID

            # Asigna la imagen a la instancia después de que se haya creado
            if 'imagen_producto' in request.FILES:
                image_file = request.FILES['imagen_producto']
                solicitud.imagen_producto.save(image_file.name, ContentFile(image_file.read()), save=True)

            aux['msj'] = "¡Solicitud enviada correctamente!"
        else:
            aux['form'] = form
            aux['msj'] = "¡El formulario no es valido!"
            
    return render(request, 'core/miembros/solicitudes/requestP.html', aux)
def solicitudA(request):
    aux = {'form': SolicitudAForm()}
    
    if request.method == 'POST':
        form = SolicitudAForm(request.POST, request.FILES)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.imagen_artista = None  # Asegúrate de que la imagen no se guarde en este punto
            solicitud.save()  # Guarda la instancia primero para obtener un ID

            # Asigna la imagen a la instancia después de que se haya creado
            if 'imagen_artista' in request.FILES:
                image_file = request.FILES['imagen_artista']
                solicitud.imagen_artista.save(image_file.name, ContentFile(image_file.read()), save=True)

            aux['msj'] = "¡Solicitud enviada correctamente!"
        else:
            aux['form'] = form
            aux['msj'] = "¡El formulario no es valido!"
            
    return render(request, 'core/miembros/solicitudes/requestA.html', aux)
def editar_solicitud_p(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudP, pk=solicitud_id)
    if solicitud.estado in('E', 'R'):
        aux = {'form': SolicitudPForm(instance=solicitud)
        }

        if request.method == 'POST':
            if 'imagen_producto' in request.FILES:
                    if solicitud.imagen_producto:
                        if os.path.isfile(solicitud.imagen_producto.path):
                            os.remove(solicitud.imagen_producto.path)
                            solicitud.imagen_producto.delete(save=False)
            form = SolicitudPForm(request.POST, request.FILES, instance=solicitud)
            if form.is_valid():
                if solicitud.estado == 'R':
                    solicitudRechazada = get_object_or_404(SolicitudesRechazadas, solicitudP=solicitud)
                    solicitudRechazada.delete()
                    solicitud.estado = 'E'
                    solicitud.save()
                    form.save()
                else:
                    solicitud.save()
                    form.save()
                aux['msj'] = "¡Solicitud actualizada correctamente!"
            else:
                aux['form'] = form
                aux['msj'] = "¡Error al actualizar su solicitud!"
    else:
        return redirect('miembros')
    return render(request, 'core/miembros/crud/updateP.html', aux)
def editar_solicitud_a(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudA, pk=solicitud_id)
    if solicitud.estado in('E', 'R'):
        aux = {'form': SolicitudAForm(instance=solicitud)
        }

        if request.method == 'POST':
            if 'imagen_artista' in request.FILES:
                    if solicitud.imagen_artista:
                        if os.path.isfile(solicitud.imagen_artista.path):  # Verifica si el archivo existe en el sistema de archivos
                            os.remove(solicitud.imagen_artista.path)
                            solicitud.imagen_artista.delete(save=False)
            form = SolicitudAForm(request.POST, request.FILES, instance=solicitud)
            if form.is_valid():
                if solicitud.estado == 'R':
                    solicitudRechazada = get_object_or_404(SolicitudesRechazadas, solicitudA=solicitud)
                    solicitudRechazada.delete()
                    solicitud.estado = 'E'
                    solicitud.save()
                    form.save()
                else:
                    solicitud.save()
                    form.save()
                aux['msj'] = "¡Solicitud actualizada correctamente!"
            else:
                aux['form'] = form
                aux['msj'] = "¡Error al actualizar su solicitud!"
    else:
        return redirect('miembros')
    return render(request, 'core/miembros/crud/updateA.html', aux)

#VISTAS DE ADMINISTRADORES
def administradores(request):
    if request.user.is_authenticated:
        if request.user.tipo_usuario.nom_tipo == 'comun' or request.user.tipo_usuario.nom_tipo == 'miembro':
            return redirect('index')
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
        solicitudA = SolicitudA.objects.filter(estado='E')
        solicitudP = SolicitudP.objects.filter(estado='E')
        aux = {
            'listaA' : solicitudA,
            'listaP' : solicitudP,
        }

        return render(request, 'core/administradores/admin.html', aux)
    else:
        return redirect('index')
def rechazar_solicitud_a(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudA, pk=solicitud_id)
    aux = {'form': SolicitudesRechazadasAForm(initial={'solicitudA': solicitud})}
    if request.method == 'POST':
        form = SolicitudesRechazadasAForm(request.POST, initial={'solicitudA': solicitud})
        if form.is_valid():
            solicitud.estado = 'R'
            solicitud_rechazada = form.save(commit=False)
            # Asignar la solicitud asociada
            solicitud_rechazada.solicitudA = solicitud
            # Guardar la instancia en la base de datos
            solicitud_rechazada.save()
            solicitud.save()
            aux['msj'] = "Solicitud rechazada correctamente."
            return redirect('administradores')
        else:
            aux['form'] = form
    return render(request, 'core/administradores/solicitudes/rechazarA.html', aux)
def rechazar_solicitud_p(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudP, pk=solicitud_id)
    aux = {'form': SolicitudesRechazadasPForm(initial={'solicitudP': solicitud})}
    if request.method == 'POST':
        form = SolicitudesRechazadasPForm(request.POST, initial={'solicitudP': solicitud})
        if form.is_valid():
            solicitud.estado = 'R'
            solicitud_rechazada = form.save(commit=False)
            # Asignar la solicitud asociada
            solicitud_rechazada.solicitudP = solicitud
            # Guardar la instancia en la base de datos
            solicitud_rechazada.save()
            solicitud.save()
            aux['msj'] = "Solicitud rechazada correctamente."
            return redirect('administradores')
        else:
            aux['form'] = form
    return render(request, 'core/administradores/solicitudes/rechazarP.html', aux)
def aprobar_solicitud_a(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudA, pk=solicitud_id)
    form = AprobarSolicitudForm(request.POST or None, initial={'solicitud_id': solicitud_id})
    msj = ""  # Inicializa la variable del mensaje
    if request.method == 'POST':
        if form.is_valid():
            solicitud.estado = 'A'
            artista = Artista(
                nombre=solicitud.nombre_artista,
                fecha_nacimiento=solicitud.fecha_nacimiento_artista,
                biografia=solicitud.biografia_artista,
                sitio_web=solicitud.sitio_web_artista
            )
            artista.save()
            # Copiar la imagen de la solicitud a la ubicación de almacenamiento de artistas
            if solicitud.imagen_artista:
                nombre_archivo = os.path.basename(solicitud.imagen_artista.name)
                ruta_artista = os.path.join('artistas', artista.nombre, nombre_archivo)
                os.makedirs(os.path.dirname(ruta_artista), exist_ok=True)
                with open(solicitud.imagen_artista.path, 'rb') as origen, open(ruta_artista, 'wb') as destino:
                    shutil.copyfileobj(origen, destino)
                artista.imagen = ruta_artista
                artista.save()
                
                # Eliminar archivo original en la ruta de origen
                os.remove(solicitud.imagen_artista.path)  # <---- Aquí se elimina el archivo original
                
                solicitud.imagen_artista.delete()
                
            solicitud.save()
            msj = "¡Solicitud aprobada y Artista agregado correctamente!"
            return redirect('administradores')
        else:
            msj = "Hubo un problema al procesar el formulario."
    return render(request, 'core/administradores/solicitudes/aprobarA.html', {'form': form, 'solicitud': solicitud, 'msj': msj})
def aprobar_solicitud_p(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudP, pk=solicitud_id)
    form = AprobarSolicitudForm(request.POST or None, initial={'solicitud_id': solicitud_id})
    msj = ""  # Inicializa la variable del mensaje
    if request.method == 'POST':
        form = AprobarSolicitudForm(request.POST)
        if form.is_valid():
            solicitud.estado = 'A'
            tipo = get_object_or_404(TipoProducto, nom_tipo=solicitud.tipo_producto)
            producto = Producto(
                titulo=solicitud.nombre_producto,
                descripcion=solicitud.descripcion_producto,
                artista=solicitud.artista_producto,
                tipo=tipo,
                precio=solicitud.precio_producto
            )
            producto.save()
            if solicitud.imagen_producto:
                nombre_archivo = os.path.basename(solicitud.imagen_producto.name)
                ruta_producto = os.path.join('productos', producto.artista.nombre, producto.titulo, nombre_archivo)
                os.makedirs(os.path.dirname(ruta_producto), exist_ok=True)
                with open(solicitud.imagen_producto.path, 'rb') as origen, open(ruta_producto, 'wb') as destino:
                    shutil.copyfileobj(origen, destino)
                producto.imagen = ruta_producto
                producto.save()
                # Eliminar archivo original en la ruta de origen
                os.remove(solicitud.imagen_producto.path)  # <---- Aquí se elimina el archivo original
                solicitud.imagen_producto.delete()
            solicitud.save()
            if producto.tipo.nom_tipo == "cancion":
                msj = f"¡Solicitud aprobada y {producto.tipo.nom_tipo} agregada correctamente!"
            else:
                msj = f"¡Solicitud aprobada y {producto.tipo.nom_tipo} agregado correctamente!"
            return redirect('administradores')
        else:
            msj = "Hubo un problema al procesar el formulario."
    return render(request, 'core/administradores/solicitudes/aprobarP.html', {'form': form, 'solicitud': solicitud, 'msj': msj})
def agregar_artista(request):
    aux = {'form': ArtistaForm()}

    if request.method == 'POST':
        form = ArtistaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            aux['msj'] = "¡Artista agregado con éxito!"
        else:
            aux['form'] = form
            aux['msj'] = "¡El formulario no es valido!"
    return render(request, 'core/administradores/crud/addA.html', aux)
def editar_artista(request, artista_id):
    artista = get_object_or_404(Artista, pk=artista_id)
    aux = {
        'form': ArtistaForm(instance=artista)
    }
    if request.method == 'POST':
        if 'imagen' in request.FILES:
            if artista.imagen:
                if os.path.isfile(artista.imagen.path):
                    os.remove(artista.imagen.path)
                    artista.imagen.delete(save=False)
        form = ArtistaForm(request.POST, request.FILES, instance=artista)
        if form.is_valid():
            form.save()
            aux['msj'] = "¡Artista actualizado correctamente!"
            return redirect('administradores')
        else:
            aux['form'] = form
            aux['msj'] = "¡El formulario no es valido!"
    return render(request, 'core/administradores/crud/updateA.html', aux)
def quitar_imagen_artista(request, artista_id):
    artista = get_object_or_404(Artista, pk=artista_id)
    if artista.imagen:
                if os.path.isfile(artista.imagen.path):
                    os.remove(artista.imagen.path)
                    artista.imagen.delete(save=False)
                    artista.save()
                    messages.success(request, 'La imágen fue eliminada correctamente.')
                    return redirect('administradores')
def eliminar_artista(request, artista_id):
    artista = Artista.objects.get(pk=artista_id)
    artista.delete()
    messages.success(request, 'Artista eliminado correctamente.')
    return redirect('administradores')
def enable_or_disable_artista(request, artista_id):
    artista = get_object_or_404(Artista, pk=artista_id)
    frase = ""
    if artista.habilitado:
        artista.habilitado = False
        frase = "deshabilitado"
    else:
        artista.habilitado = True
        frase = "habilitado"
    artista.save()
    
    # Devolver una respuesta JSON con un mensaje y el nuevo estado del artista
    data = {
        'message': f'¡Artista {frase} con éxito!',
        'habilitado': artista.habilitado
    }
    return JsonResponse(data)
def agregar_producto(request):
    if not TipoProducto.objects.exists():
        tipos = ['cancion', 'album', 'ep']  # Reemplaza esto con tus tipos de productos
        for tipo in tipos:
            TipoProducto.objects.create(nom_tipo=tipo)
    aux = {'form': ProductoForm()}

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            aux['msj'] = "¡Producto agregado con éxito!"
        else:
            aux['form'] = form
            aux['msj'] = "¡El formulario no es valido!"
    return render(request, 'core/administradores/crud/addP.html', aux)
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    aux = {
        'form': ProductoForm(instance=producto)
    }
    if request.method == 'POST':
        if 'imagen' in request.FILES:
            if producto.imagen:
                if os.path.isfile(producto.imagen.path):
                    os.remove(producto.imagen.path)
                    producto.imagen.delete(save=False)
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            aux['msj'] = "¡Producto actualizado correctamente!"
        else:
            aux['form'] = form
            aux['msj'] = "¡El formulario no es valido!"
    return render(request, 'core/administradores/crud/updateP.html', aux)
def eliminar_producto(request, producto_id):
    producto = Producto.objects.get(pk=producto_id)
    producto.delete()
    messages.success(request, 'Producto eliminado correctamente.')
    return redirect('administradores')
def enable_or_disable_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    frase = ""
    if producto.habilitado:
        producto.habilitado = False
        frase = "deshabilitado"
    else:
        producto.habilitado = True
        frase = "habilitado"
    producto.save()
    
    # Devolver una respuesta JSON con un mensaje y el nuevo estado del producto
    data = {
        'message': f'¡Producto {frase} con éxito!',
        'habilitado': producto.habilitado
    }
    return JsonResponse(data)
def listar_para_administradores(request):
    messages.get_messages(request).used = True
    tipo = get_object_or_404(TipoUsuario, nom_tipo='miembro')
    aux = {
        'artistas': Artista.objects.all(),
        'productos': Producto.objects.all(),
        'miembros': Usuario.objects.filter(tipo_usuario=tipo)
    }
    return render(request, 'core/administradores/crud/list.html', aux)
def agregar_miembro(request):
    storage = messages.get_messages(request)
    storage.used = True
    aux = { 'form': registerForm()
    }
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            tipo = get_object_or_404(TipoUsuario, nom_tipo='miembro')
            user = form.save(commit=False)
            user.tipo_usuario = tipo
            user.save()
            group, created = Group.objects.get_or_create(name='miembro')
            user.groups.add(group)
            user.save()
            messages.success(request, f'Cuenta para el miembro #{user.pk}-{user.username} agregada correctamente!')
            return redirect('administradores')
        else:
            aux['form'] = form
            messages.error(request, 'El form no es valido!')
    return render(request, 'core/administradores/crud/miembros_add.html', aux)
def editar_miembro(request, miembro_id):
    storage = messages.get_messages(request)
    storage.used = True
    miembro = get_object_or_404(Usuario, pk=miembro_id)
    aux = { 'form': MiembroForm(instance=miembro) 
    }
    if request.method == 'POST':
        form = MiembroForm(request.POST, instance=miembro)
        if form.is_valid():
            miembro.set_password(form.cleaned_data['password'])
            try:
                miembro.save()
                messages.success(request, 'Contraseña actualizada correctamente.')
            except Exception as e:
                messages.error(request, 'Contraseña no actualizada. Error: {}'.format(e))
            return redirect('administradores')
        else:
            aux['form'] = form
            messages.error(request, 'El form no es valido!')
            #aux['msj'] = "¡La contraseña no es valida!"
    return render(request, 'core/administradores/crud/updateM.html', aux)
def eliminar_miembro(request, miembro_id):
    storage = messages.get_messages(request)
    storage.used = True
    miembro = get_object_or_404(Usuario, pk=miembro_id)
    try:
        miembro.delete()
    except Exception as e:
        print(e)
        messages.error(request, 'No se pudo eliminar al miembro!')
        return redirect('administradores')
    messages.success(request, '¡Miembro eliminado correctamente!')
    return redirect('administradores')
def enable_or_disable_miembro(request, miembro_id):
    miembro = get_object_or_404(Usuario, pk=miembro_id)
    frase = ""
    if miembro.is_active:
        miembro.is_active = False
        frase = "deshabilitado"
    else:
        miembro.is_active = True
        frase = "habilitado"
    miembro.save()

    # Devolver una respuesta JSON con un mensaje y el nuevo estado del producto
    data = {
        'message': f'¡Miembro {frase} con éxito!',
        'habilitado': miembro.is_active
    }
    return JsonResponse(data)