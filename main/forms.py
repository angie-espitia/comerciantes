from django import forms

from .models import Producto

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = ('__all__' )
        exclude = ('codigo',)
        labels = { 'nombre': 'Nombre del Producto', 
        			'stock': 'stock', 
        			'valor_costo': 'valor_costo', 
        			'valor_venta': 'venta', 
        			'descripcion': 'descripcion', 
        		  }
        widgets = { 'nombre': forms.TextInput(attrs={'class':'form-control'}),
        			'stock': forms.TextInput(attrs={'class':'form-control'}),
        			'valor_costo': forms.TextInput(attrs={'class':'form-control'}),
        			'valor_venta': forms.TextInput(attrs={'class':'form-control'}),
        			'descripcion': forms.Textarea(attrs={'class':'form-control'}),
				}