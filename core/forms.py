from django import forms
from .models import *

class ArtistaForm(forms.ModelForm):
    class Meta:
        model = Artista
        fields = '__all__'

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'

class SolicitudForm(forms.ModelForm):
    artista = forms.ModelChoiceField(queryset=Artista.objects.filter(habilitado=True), widget=forms.Select(attrs={'class': 'form-control'}))
    class Meta:
        model = Solicitud
        fields = ['nombre_producto', 'descripcion_producto', 'imagen_producto', 'tipo_producto', 'precio_producto',]
        widgets = {
            'imagen_producto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def __init__(self, *args, **kwargs):
        super(SolicitudForm, self).__init__(*args, **kwargs)