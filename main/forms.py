from django import forms

from .models import Producto, Compra, detalle_compra, detalle_usuario_producto, Proveedor
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

    def __init__(self, *args, **kwargs):
        super(ProductoForm_dos, self).__init__(*args, **kwargs)
        self.fields['descripcion'].required = False  # solo con los campos que especificaste en la clase Meta
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class DetalleUsuarioProductoForm(forms.ModelForm):

    class Meta:
        model = detalle_usuario_producto
        fields = ('proveedor_id', )

    def __init__(self, *args, **kwargs):
        super(DetalleUsuarioProductoForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

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
        usuario = kwargs.pop('user')     # client is the parameter passed from views.py
        usuario_proveedor = detalle_usuario_producto.objects.filter(usuario_id=usuario.id, producto_id__isnull=True)
        usuario_producto = detalle_usuario_producto.objects.filter(usuario_id=usuario.id, producto_id__isnull=False)
        array_p = []
        for f in usuario_proveedor:
            array_p.append(f.proveedor_id.id)
        p = Proveedor.objects.filter(id__in=array_p)
        array_e = []
        for f in usuario_producto:
            array_e.append(f.producto_id.id)
        po = Producto.objects.filter(id__in=array_e)

        super(DetalleCompraForm, self).__init__(*args, **kwargs)
        self.fields['producto_id'].queryset= po
        self.fields['proveedor_id'].queryset= p
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

DetalleCompraFormSet = inlineformset_factory(Compra, detalle_compra, form=DetalleCompraForm, extra=1)
