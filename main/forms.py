from django import forms

from .models import Producto, Compra, detalle_compra, detalle_negocio_producto, detalle_usuario_negocio, Proveedor, Venta, detalle_venta, Pabellon, Negocio
from django.forms.models import inlineformset_factory

class NegocioForm(forms.ModelForm):

    class Meta:
        model = Negocio
        fields = ('__all__' )
        exclude = ('usuario_id', 'pabellon_id')
        labels = { 'nombre': 'Nombre del Negocio',
                    'nit': 'NIT del negocio',
                    'telefono': 'Telefono del Negocio',
                    'email': 'Email del Negocio'
                  }
        widgets = { 'nombre': forms.TextInput(attrs={'class':'form-control teli','placeholder':"Negocio" }),
                    'nit': forms.TextInput(attrs={'class':'form-control teli','placeholder':"Nit"}),
                    'telefono': forms.TextInput(attrs={'class':'form-control teli','placeholder':"Telefono",'id':'telefonoId'}),
                    'email': forms.EmailInput(attrs={'class':'form-control teli','placeholder':"Correo Electrónico",'id':'emailId'}),
                  }

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.fields['nit'].required = False
        self.fields['telefono'].required = False
        self.fields['email'].required = False

class NegocioForm_dos(forms.ModelForm):

    class Meta:
        model = Negocio
        fields = ('__all__' )
        labels = { 'nombre': 'Nombre del Negocio',
                    'nit': 'NIT del negocio',
                    'telefono': 'Telefono del Negocio',
                    'email': 'Email del Negocio',
                    'pabellon_id': 'Pabellón'
                  }
        widgets = { 'nombre': forms.TextInput(attrs={'class':'form-control'}),
                    'nit': forms.TextInput(attrs={'class':'form-control'}),
                    'telefono': forms.TextInput(attrs={'class':'form-control','id':'telefonoId'}),
                    'email': forms.EmailInput(attrs={'class':'form-control','id':'emailId'}),
                  }

    def __init__(self, *args, **kwargs):
        super(NegocioForm_dos, self).__init__(*args, **kwargs)
        self.fields['nit'].required = False
        self.fields['telefono'].required = False
        self.fields['email'].required = False
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control teli'
            })

class DetalleUsuarioNegocioForm(forms.ModelForm):

    class Meta:
        model = detalle_usuario_negocio
        fields = ('usuario_id', )
        exclude = ( )

    def __init__(self, *args, **kwargs):
        super(DetalleUsuarioNegocioForm, self).__init__(*args, **kwargs)
        # self.fields['negocio_id'].required = False
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class PabellonForm(forms.ModelForm):

    class Meta:
        model = Pabellon
        fields = ('__all__' )
        labels = { 'nombre': 'Nombre del Pabellon',
                    'descripcion': 'Descripcion',
                  }
        widgets = { 'nombre': forms.TextInput(attrs={'class':'form-control','placeholder':"Pabellon" }),
                    'descripcion': forms.Textarea(attrs={'class':'form-control','placeholder':"Descripcion" }),
                }

    def __init__(self, *args, **kwargs):
        super(PabellonForm, self).__init__(*args, **kwargs)
        self.fields['descripcion'].required = False

class ProductoForm(forms.ModelForm):

    class Meta:
        model = Producto
        fields = ('__all__' )
        exclude = ('imagen','estado')
        labels = { 'nombre': 'Nombre del Producto',
        			'stock': 'Stock',
        			'valor_costo': 'valor del costo',
        			'valor_venta': 'Precio de venta',
        			'descripcion': 'Descripcion',
                    'unidad_medida_id': 'Unidad de Medida'
        		  }

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        # asi vuelves tus campos no requeridos
        self.fields['descripcion'].required = False  # solo con los campos que especificaste en la clase Meta
        self.fields['stock'].widget.attrs['min'] = 1
        self.fields['valor_costo'].widget.attrs['min'] = 1
        self.fields['valor_costo'].widget.attrs['id'] = 'costo_id'
        self.fields['valor_venta'].widget.attrs['min'] = 1
        self.fields['valor_venta'].widget.attrs['id'] = 'venta_id'
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control teli'
            })

class ProductoForm_dos(forms.ModelForm):

    class Meta:
        model = Producto
        fields = ('__all__' )
        exclude = ( )

    def __init__(self, *args, **kwargs):
        super(ProductoForm_dos, self).__init__(*args, **kwargs)
        self.fields['descripcion'].required = False
        self.fields['imagen'].required = False
        self.fields['stock'].widget.attrs['min'] = 0
        self.fields['valor_costo'].widget.attrs['min'] = 1
        self.fields['valor_costo'].widget.attrs['id'] = 'costo_id'
        self.fields['valor_venta'].widget.attrs['min'] = 1
        self.fields['valor_venta'].widget.attrs['id'] = 'venta_id'
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control teli'
            })

class DetalleNegocioProductoForm(forms.ModelForm):

    class Meta:
        model = detalle_negocio_producto
        fields = ('proveedor_id', )

    def __init__(self, *args, **kwargs):
        negocio = kwargs.pop('user')     # client is the parameter passed from views.py
        producto = kwargs.pop('producto')
        negocio_proveedor = detalle_negocio_producto.objects.filter(negocio_id=negocio, producto_id__isnull=True)
        array_p = []
        for f in negocio_proveedor:
            array_p.append(f.proveedor_id.id)
        p = Proveedor.objects.filter(id__in=array_p)

        proveedor_ini = detalle_negocio_producto.objects.filter(negocio_id=negocio,producto_id=producto)
        for x in proveedor_ini:
            pr = x.proveedor_id

        super(DetalleNegocioProductoForm, self).__init__(*args, **kwargs)
        self.fields['proveedor_id'].queryset= p
        self.initial['proveedor_id'] = pr

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
        # self.fields['total'].widget.attrs['disabled'] = True
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control teli'
            })

class DetalleCompraForm(forms.ModelForm):

    class Meta:
        model = detalle_compra
        fields = ('__all__' )
        exclude = ('cantidad_stock_anterior','cantidad_stock_momento',)

    def __init__(self, *args, **kwargs):
        negocio = kwargs.pop('user')     # client is the parameter passed from views.py
        usuario_proveedor = detalle_negocio_producto.objects.filter(negocio_id=negocio, producto_id__isnull=True)
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio, producto_id__isnull=False)
        array_p = []
        for f in usuario_proveedor:
            array_p.append(f.proveedor_id.id)
        p = Proveedor.objects.filter(id__in=array_p)
        array_e = []
        for f in negocio_producto:
            array_e.append(f.producto_id.id)
        po = Producto.objects.filter(id__in=array_e, estado='1').order_by('nombre')

        super(DetalleCompraForm, self).__init__(*args, **kwargs)
        self.fields['producto_id'].queryset= po
        self.fields['proveedor_id'].queryset= p
        self.fields['cantidad'].widget.attrs['min'] = 1
        self.fields['valor_unitario'].widget.attrs['min'] = 1
        self.fields['total_producto'].widget.attrs['min'] = 1
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

DetalleCompraFormSet = inlineformset_factory(Compra, detalle_compra, form=DetalleCompraForm, extra=1)


class VentaForm(forms.ModelForm):

    class Meta:
        model = Venta
        fields = ('__all__' )
        widgets = { 'fecha': forms.DateInput(attrs={'class':'form-control', 'type':'date', 'input_formats': '%d/%m/%Y'}),
                }

    def __init__(self, *args, **kwargs):
        super(VentaForm, self).__init__(*args, **kwargs)
        self.fields['observacion'].required = False
        # self.fields['total'].widget.attrs['disabled'] = True
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class DetalleVentaForm(forms.ModelForm):

    class Meta:
        model = detalle_venta
        fields = ('__all__' )
        exclude = ('cantidad_stock_anterior','cantidad_stock_momento',)

    def __init__(self, *args, **kwargs):
        negocio = kwargs.pop('user')     # client is the parameter passed from views.py
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio, producto_id__isnull=False)
        array_e = []
        for f in negocio_producto:
            array_e.append(f.producto_id.id)
        po = Producto.objects.filter(id__in=array_e, estado='1').order_by('nombre')

        super(DetalleVentaForm, self).__init__(*args, **kwargs)
        self.fields['producto_id'].queryset= po
        self.fields['cantidad'].widget.attrs['min'] = 1
        self.fields['total_producto'].widget.attrs['min'] = 1
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
            })

DetalleVentaFormSet = inlineformset_factory(Venta, detalle_venta, form=DetalleVentaForm, extra=1)
