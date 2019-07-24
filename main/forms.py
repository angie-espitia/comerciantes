from django import forms

from .models import Producto, Compra, detalle_compra
from django.forms.models import inlineformset_factory

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = ('__all__' )
        exclude = ('codigo', 'imagen')
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

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['descripcion'].required = False  # solo con los campos que especificaste en la clase Meta

class ProductoForm_dos(forms.ModelForm):

    class Meta:
        model = Producto
        fields = ('__all__' )
        exclude = ('codigo', )

class CompraForm(forms.ModelForm):

    class Meta:
        model = Compra
        fields = ('__all__' )
        widgets = { 'fecha': forms.DateInput(attrs={'class':'form-control', 'type':'date', 'input_formats': '%d/%m/%Y'}),
                }

    def __init__(self, *args, **kwargs):
        super(CompraForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class DetalleCompraForm(forms.ModelForm):

    class Meta:
        model = detalle_compra
        fields = ('__all__' )

    def __init__(self, *args, **kwargs):
        super(DetalleCompraForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad == '':
            raise forms.ValidationError("Debe ingresar una cantidad valida")
        return cantidad

    def clean_valor_unitario(self):
        valor_unitario = self.cleaned_data['valor_unitario']
        if valor_unitario == '':
            raise forms.ValidationError("Debe ingresar un valor unitario valido")
        return valor_unitario

DetalleCompraFormSet = inlineformset_factory(Compra, detalle_compra, form=DetalleCompraForm, extra=1)