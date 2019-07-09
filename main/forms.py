from django import forms

from .models import Proveedor

class ProveedorForm(forms.ModelForm):

    class Meta:
        model = Proveedor
        fields = ('nombre', 'razon_social', 'direccion', 'telefono', 'celular', 'email')
        labels = { 'nombre': 'Nombre de la persona encargada o a contactar', 
        			'razon_social': 'Empresa', 
        			'direccion': 'Direccion', 
        			'telefono': 'Teléfono', 
        			'celular': 'Celular', 
        		  }