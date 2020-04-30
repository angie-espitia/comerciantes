from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.template import RequestContext
from main.validator import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import NoReverseMatch, reverse
from main.models import *
from main.forms import *
import json
from django.core import serializers
import datetime

def convertir_fecha(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def index(request):
    return render(request, 'pagina/index.html')

# registro de propietario y empresa
def registrar_comerciante(request):
    error = False
    if request.method == 'POST':
        validators = FormRegistroValidator(request.POST)
        validators.required = ['nombre', 'apellido', 'email', 'username', 'password1']

        if validators.is_valid():
            negocio = Negocio()
            negocio.nombre = request.POST['nombre_negocio']
            negocio.nit = request.POST['nit_negocio']
            negocio.save()

            usuario = User()
            usuario.first_name = request.POST['nombre']
            usuario.last_name = request.POST['apellido']
            usuario.email = request.POST['email']
            usuario.username = request.POST['username']
            usuario.password = make_password(request.POST['password1'])
            usuario.is_active = True
            grupo = Group.objects.get(name="propietario")
            usuario.save()
            usuario.groups.add(grupo)
            usuario.save()

            myusuario = Usuario()
            myusuario.id = usuario
            myusuario.documento = request.POST['documento']
            myusuario.negocio_id = Negocio.objects.latest('id')
            myusuario.save()

            return redirect('login')
        else:
            return render(request, 'registrar_tendero.html', {'error': validators.getMessage() } )
        # Agregar el usuario a la base de datos
    return render( request, 'registrar_tendero.html' )

def login(request):

    if request.method == 'POST':

        validators = FormLoginValidator(request.POST)

        if validators.is_valid():

            auth.login(request, validators.acceso)  # Crear una sesion
            return redirect('/principal')

        else:
            return render(request, 'login.html', {'error': validators.getMessage()} )

    return render(request, 'login.html' )

@login_required(login_url="/")
def logout(request):
    auth.logout(request)
    return redirect("/")

# ------------------------------- views manejo negocio tenderos ---------------------------------------------------------

@login_required(login_url="/")
def principal_app(request):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=usuario.negocio_id, producto_id__isnull=False)
    negocioo = []
    for x in negocio_producto:
        if x.producto_id.stock <= 9:
            negocioo.append(x)

    array_producto = []
    for f in negocio_producto:
        array_producto.append(f.producto_id.id)
    venta = Venta.objects.all()
    array_venta = []
    for f in venta:
        array_venta.append(f.id)
    detalles__ventas = detalle_venta.objects.filter(venta_id__in=array_venta, producto_id__in=array_producto)

    for x in detalles__ventas:
        print(x.cantidad)
    return render(request, 'app/index_app.html', {'negocioo':negocioo}, {'detalles__ventas': detalles__ventas})

# registro de empleados
@login_required(login_url="/")
def registrar_empleado(request, pk):
    error = False
    usuario = Usuario.objects.get(id=pk)
    negocio_actual = usuario.negocio_id
    if request.method == 'POST':
        validators = FormRegistroValidator(request.POST)
        validators.required = ['nombre', 'apellido', 'email', 'username', 'password1']

        if validators.is_valid():
            usuario = User()
            usuario.first_name = request.POST['nombre']
            usuario.last_name = request.POST['apellido']
            usuario.email = request.POST['email']
            usuario.username = request.POST['username']
            usuario.password = make_password(request.POST['password1'])
            usuario.is_active = True
            grupo = Group.objects.get(name="empleado")
            usuario.save()
            usuario.groups.add(grupo)
            usuario.save()

            myusuario = Usuario()
            myusuario.id = usuario
            myusuario.documento = request.POST['documento']
            myusuario.negocio_id = negocio_actual
            myusuario.save()

            return redirect('list_usuarios')
        else:
            return render(request, 'registrar_empleado.html', {'error': validators.getMessage() } )
        # Agregar el usuario a la base de datos
    return render( request, 'app/administracion/registrar_empleado.html' )

@login_required(login_url="/")
def perfil_usuario(request, pk):
    usuario = User.objects.get(id=pk)
    miusuario = Usuario.objects.get(id=usuario)
    error = False
    if request.method == 'POST':
        # import pdb; pdb.set_trace()
        usuario.email = request.POST.get('email')
        usuario.first_name = request.POST.get('first_name')
        usuario.last_name = request.POST.get('last_name')
        usuario.save()

        miusuario.cedula = request.POST.get('documento')
        miusuario.telefono = request.POST.get('telefono')
        miusuario.direccion = request.POST.get('direccion')
        miusuario.save()

        return HttpResponseRedirect(request.path_info) #redirige misma pag

    return render(request, 'app/administracion/perfil_usuario.html', {'usu': miusuario } )

@login_required(login_url="/")
def list_usuarios(request):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = usuario.negocio_id
    print(negocio)
    lista_usuarios = Usuario.objects.filter(negocio_id=negocio)
    for x in lista_usuarios:
        print(x)
    return render(request, 'app/administracion/lista_usuarios.html', {'usuarioss':lista_usuarios})

@login_required(login_url="/")
def modificar_contra(request, pk):
    error = False
    usuario_contra = User.objects.get(id=pk)
    if request.method == 'POST':
        usuario_contra.password = make_password(request.POST['password1'])
        usuario_contra.save()
        # log(request, "CONTRASEÑA_MODIFICADA")
        return HttpResponseRedirect(request.path_info) #redirige misma pag

# proveedor

@login_required(login_url="/")
def view_proveedor(request, pk):
    usuario = Usuario.objects.get(id=pk)
    negocio_proveedor = detalle_negocio_producto.objects.filter(negocio_id=usuario.negocio_id, producto_id__isnull=True)
    return render(request, 'app/proveedor/view_proveedor.html', {'negocio_proveedor':negocio_proveedor} )

@login_required(login_url="/")
def agregar_proveedor(request, pk):

    usu = Usuario.objects.get(id=pk)
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        if request.is_ajax():
            proveedor = Proveedor()
            proveedor.nombre = request.POST.get('nombre_proveedor')
            proveedor.razon_social = request.POST.get('razon_social_proveedor')
            proveedor.direccion = request.POST.get('direccion_proveedor')
            proveedor.telefono = request.POST.get('telefono_proveedor')
            proveedor.celular = request.POST.get('celular_proveedor')
            proveedor.email = request.POST.get('email_proveedor')
            proveedor.save()

            proveedor2 = Proveedor.objects.latest('id')
            negocio_proveedor = detalle_negocio_producto()
            negocio_proveedor.negocio_id = usu.negocio_id
            negocio_proveedor.proveedor_id = proveedor2
            negocio_proveedor.save()
            return HttpResponse('ok')

    return render(request, 'app/proveedor/agregar_proveedor.html' )

@login_required(login_url="/")
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == "POST" and request.is_ajax():
        # import pdb; pdb.set_trace()
        proveedor.nombre = request.POST.get('nombre_proveedor')
        proveedor.razon_social = request.POST.get('razon_social_proveedor')
        proveedor.direccion = request.POST.get('direccion_proveedor')
        proveedor.telefono = request.POST.get('telefono_proveedor')
        proveedor.celular = request.POST.get('celular_proveedor')
        proveedor.email = request.POST.get('email_proveedor')
        proveedor.save()
        return HttpResponse('ok')
    else:
        dic = {
            'id':proveedor.id,
            'nombre':proveedor.nombre,
            'razon_social':proveedor.razon_social,
            'email':proveedor.email,
            'telefono':proveedor.telefono,
            'direccion':proveedor.direccion,
            'celular':proveedor.celular
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    negocio_proveedor = get_object_or_404(detalle_negocio_producto, proveedor_id=proveedor.id)
    if request.method == "POST" and request.is_ajax():
        negocio_proveedor.delete()
        proveedor.delete()

        return HttpResponse('ok')
    else:
        dic = {
            'id':proveedor.id,
            'razon_social':proveedor.razon_social,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

# producto
@login_required(login_url="/")
def view_producto(request, pk):

    usuario = Usuario.objects.get(id=pk)
    negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=usuario.negocio_id, producto_id__isnull=False)

    return render(request, 'app/producto/view_producto.html', {'negocio_producto':negocio_producto} )

@login_required(login_url="/")
def agregar_producto(request, pk):

    usuario = Usuario.objects.get(id=pk)
    negocio_proveedor = detalle_negocio_producto.objects.filter(negocio_id=usuario.negocio_id, producto_id__isnull=True)
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.save()

            producto2 = Producto.objects.latest('id')
            proveedor_recibido = request.POST.get('negocio_proveedor')
            proveedor_p = Proveedor.objects.get(id=proveedor_recibido)

            negocio_producto = detalle_negocio_producto()
            negocio_producto.negocio_id = usuario.negocio_id
            negocio_producto.producto_id = producto2
            negocio_producto.proveedor_id = proveedor_p
            negocio_producto.save()

            producto2.imagen = request.FILES.get('imagen')
            producto2.save()

            return redirect('view_producto', pk=usuario.pk)
    else:
        form = ProductoForm()

    return render(request, 'app/producto/agregar_producto.html', {'form' : form, 'negocio_proveedor': negocio_proveedor } )

@login_required(login_url="/")
def detalle_producto(request, pk):
    producto_recibido = get_object_or_404(Producto, pk=pk)
    detalle_producto_negocio = detalle_negocio_producto.objects.filter(producto_id=producto_recibido.id)
    for row in detalle_producto_negocio:
        d_p_u = get_object_or_404(detalle_negocio_producto, pk=row.id)
        negocioo = d_p_u.negocio_id.id
    print(negocioo)
    detalle_compra_producto = detalle_compra.objects.filter(producto_id=producto_recibido.id)

    if request.method == "POST":
        form = ProductoForm_dos(request.POST, request.FILES, instance=producto_recibido)
        form2 = DetalleNegocioProductoForm(request.POST, user=negocioo)
        if form.is_valid() and form2.is_valid():
            producto = form.save(commit=False)
            producto.save()
            producto2 = form2.save(commit=False)
            producto2.save()

            return HttpResponseRedirect(request.path_info) #redirige misma pag
    else:
        form = ProductoForm_dos(instance=producto_recibido)
        form2 = DetalleNegocioProductoForm(user=negocioo)
    return render(request, 'app/producto/editar_producto.html', {'detalle_producto_negocio':detalle_producto_negocio, 'detalle_compra_producto':detalle_compra_producto, 'form' : form, 'form2':form2} )

@login_required(login_url="/")
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    negocio_producto = get_object_or_404(detalle_negocio_producto, producto_id=producto.id)
    if request.method == "POST" and request.is_ajax():
        negocio_producto.delete()
        producto.delete()

        return HttpResponse('ok')
    else:
        dic = {
            'id':producto.id,
            'nombre':producto.nombre,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

# compras
@login_required(login_url="/")
def view_de_compra(request):
    return render(request, 'app/compra/view_compra.html')

@login_required(login_url="/")
def list_compras(request, pk):
    usuario = Usuario.objects.get(id=pk)
    negocio_proveedor = detalle_negocio_producto.objects.filter(negocio_id=usuario.negocio_id, producto_id__isnull=True)
    array_proveedor = []
    for f in negocio_proveedor:
        array_proveedor.append(f.proveedor_id.id)
    compra = Compra.objects.all()
    array_compra = []
    for f in compra:
        array_compra.append(f.id)
    detalles__compras = detalle_compra.objects.filter(compra_id__in=array_compra, proveedor_id__in=array_proveedor)
    dic = {}
    var = -1
    for i in detalles__compras:
        if i.compra_id.id == var:
            var = i.compra_id.id
        else:
            dic[i.compra_id.id] = {
                'id_compra':i.compra_id.id,
                'fecha':convertir_fecha(i.compra_id.fecha),
                'proveedor':i.proveedor_id.razon_social,
                'total':i.compra_id.total,
            }
            var = i.compra_id.id
    return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def detalle_de_compra(request, pk):
    detalles__compras = detalle_compra.objects.filter(compra_id=pk)
    compra = Compra.objects.filter(id=pk)
    return render(request, 'app/compra/detalle_compra.html', {'detalles__compras' : detalles__compras, 'compra' : compra })

@login_required(login_url="/")
def editar_item_detalle_compra(request, pk):
    item_detalle_compra = get_object_or_404(detalle_compra, pk=pk)
    if request.method == "POST" and request.is_ajax():
        cantidad_actual = int(item_detalle_compra.cantidad)
        total_actual = int(item_detalle_compra.total_producto)

        item_detalle_compra.cantidad = request.POST.get('cantidad_item')
        item_detalle_compra.valor_unitario = request.POST.get('valor_unitario_item')
        item_detalle_compra.total_producto = request.POST.get('total_item')
        item_detalle_compra.save()

        cantidad_item = int(item_detalle_compra.cantidad)
        if cantidad_actual != cantidad_item:
            producto_stock = Producto.objects.get(id=item_detalle_compra.producto_id.id)
            cantidad_stock = producto_stock.stock
            resta_cantidad_stock = cantidad_stock - cantidad_actual
            # producto_stock.stock = resta_cantidad_stock
            sum_stock = resta_cantidad_stock + cantidad_item
            producto_stock.stock = sum_stock
            producto_stock.save()

        total_item = int(item_detalle_compra.total_producto)
        if total_actual != total_item:
            compra_total =  Compra.objects.get(id=item_detalle_compra.compra_id.id)
            total_compra = compra_total.total
            resta_total_compra = total_compra - total_actual
            sum_total = resta_total_compra + total_item
            compra_total.total = sum_total
            compra_total.save()

        return HttpResponse('ok')
    else:
        dic = {
            'idd':item_detalle_compra.id,
            'producto':item_detalle_compra.producto_id.nombre,
            'cantidad':item_detalle_compra.cantidad,
            'valor_unitario':item_detalle_compra.valor_unitario,
            'total':item_detalle_compra.total_producto,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def eliminar_item_detalle_compra(request, pk):
    item_detalle_compra = get_object_or_404(detalle_compra, pk=pk)
    if request.method == "POST" and request.is_ajax():
        producto_stock = Producto.objects.get(id=item_detalle_compra.producto_id.id)
        cantidad_item = item_detalle_compra.cantidad
        cantidad_stock = item_detalle_compra.producto_id.stock
        resta_stock = cantidad_stock - cantidad_item
        producto_stock.stock = resta_stock
        producto_stock.save()

        compra_total =  Compra.objects.get(id=item_detalle_compra.compra_id.id)
        total_item = item_detalle_compra.total_producto
        total_compra = compra_total.total
        resta_total = total_compra - total_item
        compra_total.total = resta_total
        compra_total.save()

        item_detalle_compra.delete()

        return HttpResponse('ok')
    else:
        dic = {
            'id':item_detalle_compra.id,
            'nombre':item_detalle_compra.producto_id.nombre,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def agregar_compra(request, pk):
    usuario = Usuario.objects.get(id=pk)
    detalle_producto_negocio = detalle_negocio_producto.objects.filter(negocio_id=usuario.negocio_id, producto_id__isnull=True)
    for row in detalle_producto_negocio:
        negocioo = row.negocio_id.id
    print(negocioo)
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        form = CompraForm(request.POST)
        detalle_compra_form_set = DetalleCompraFormSet(request.POST, form_kwargs={'user': negocioo})
        if form.is_valid() and detalle_compra_form_set.is_valid():
            compra = form.save(commit=False)
            compra.save()
            detalle_compra_form_set.instance = compra
            detalle_compra_form_set.save()

            compra_stock = detalle_compra.objects.filter(compra_id=compra)
            for row in compra_stock:
                producto_stock = Producto.objects.get(id=row.producto_id.id)
                cantidad_compra = row.cantidad
                cantidad_stock = producto_stock.stock
                sum_stock = cantidad_compra + cantidad_stock
                producto_stock.stock = sum_stock
                producto_stock.save()

            return redirect('view_compra')
    else:
        form = CompraForm()
        detalle_compra_formset=DetalleCompraFormSet(form_kwargs={'user': negocioo}) # pass parameter to the form

    return render(request, 'app/compra/agregar_compra.html', {'form' : form, 'detalle_compra_formset': detalle_compra_formset } )

@login_required(login_url="/")
def eliminar_compra(request, pk):
    compra_recibida = get_object_or_404(Compra, pk=pk)
    if request.method == "POST" and request.is_ajax():
        detalle_de_compra = detalle_compra.objects.filter(compra_id=compra_recibida.id)
        for item in detalle_de_compra:
            producto_stock = Producto.objects.get(id=item.producto_id.id)
            cantidad_item = item.cantidad
            cantidad_stock = item.producto_id.stock
            resta_stock = cantidad_stock - cantidad_item
            producto_stock.stock = resta_stock
            producto_stock.save()
            item.delete()

        compra_recibida.delete()

        return HttpResponse('ok')
    else:
        dic = {
            'idd':compra_recibida.id,
            'fecha':convertir_fecha(compra_recibida.fecha),
            'total':compra_recibida.total,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

# venta
@login_required(login_url="/")
def view_de_venta(request):
    return render(request, 'app/venta/view_venta.html')

@login_required(login_url="/")
def view_de_reportes_venta(request):
    return render(request, 'app/venta/view_reportes_venta.html')

@login_required(login_url="/")
def list_ventas(request, pk):
    usuario = Usuario.objects.get(id=pk)
    negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=usuario.negocio_id, producto_id__isnull=False)
    array_producto = []
    for f in negocio_producto:
        array_producto.append(f.producto_id.id)
    venta = Venta.objects.all()
    array_venta = []
    for f in venta:
        array_venta.append(f.id)
    detalles__ventas = detalle_venta.objects.filter(venta_id__in=array_venta, producto_id__in=array_producto)
    dic = {}
    var = -1
    for i in detalles__ventas:
        if i.venta_id.id == var:
            var = i.venta_id.id
        else:
            dic[i.venta_id.id] = {
                'id_venta':i.venta_id.id,
                'fecha':convertir_fecha(i.venta_id.fecha),
                'total':i.venta_id.total,
            }
            var = i.venta_id.id
    return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def detalle_de_venta(request, pk):
    detalles__ventas = detalle_venta.objects.filter(venta_id=pk)
    venta = Venta.objects.filter(id=pk)
    return render(request, 'app/venta/detalle_venta.html', {'detalles__ventas' : detalles__ventas, 'venta' : venta })

@login_required(login_url="/")
def editar_item_detalle_venta(request, pk):
    item_detalle_venta = get_object_or_404(detalle_venta, pk=pk)
    if request.method == "POST" and request.is_ajax():
        cantidad_actual = int(item_detalle_venta.cantidad)
        total_actual = int(item_detalle_venta.total_producto)

        item_detalle_venta.cantidad = request.POST.get('cantidad_item')
        item_detalle_venta.valor_unitario = request.POST.get('valor_unitario_item')
        item_detalle_venta.total_producto = request.POST.get('total_item')
        item_detalle_venta.save()

        cantidad_item = int(item_detalle_venta.cantidad)
        if cantidad_actual != cantidad_item:
            producto_stock = Producto.objects.get(id=item_detalle_venta.producto_id.id)
            cantidad_stock = producto_stock.stock
            suma_cantidad_stock = cantidad_stock + cantidad_actual
            # producto_stock.stock = suma_cantidad_stock
            resta_stock = suma_cantidad_stock - cantidad_item
            producto_stock.stock = resta_stock
            producto_stock.save()

        total_item = int(item_detalle_venta.total_producto)
        if total_actual != total_item:
            venta_total =  Venta.objects.get(id=item_detalle_venta.venta_id.id)
            total_venta = venta_total.total
            resta_total_venta = total_venta - total_actual
            sum_total = resta_total_venta + total_item
            venta_total.total = sum_total
            venta_total.save()

        return HttpResponse('ok')
    else:
        dic = {
            'idd':item_detalle_venta.id,
            'producto':item_detalle_venta.producto_id.nombre,
            'cantidad':item_detalle_venta.cantidad,
            # 'valor_unitario':item_detalle_venta.valor_unitario,
            'total':item_detalle_venta.total_producto,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def eliminar_item_detalle_venta(request, pk):
    item_detalle_venta = get_object_or_404(detalle_venta, pk=pk)
    if request.method == "POST" and request.is_ajax():
        producto_stock = Producto.objects.get(id=item_detalle_venta.producto_id.id)
        cantidad_item = item_detalle_venta.cantidad
        cantidad_stock = item_detalle_venta.producto_id.stock
        suma_stock = cantidad_stock + cantidad_item
        producto_stock.stock = suma_stock
        producto_stock.save()

        venta_total =  Venta.objects.get(id=item_detalle_venta.venta_id.id)
        total_item = item_detalle_venta.total_producto
        total_venta = venta_total.total
        resta_total = total_venta - total_item
        venta_total.total = resta_total
        venta_total.save()

        item_detalle_venta.delete()

        return HttpResponse('ok')
    else:
        dic = {
            'id':item_detalle_venta.id,
            'nombre':item_detalle_venta.producto_id.nombre,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def agregar_venta(request, pk):
    usuario = Usuario.objects.get(id=pk)
    detalle_producto_negocio = detalle_negocio_producto.objects.filter(negocio_id=usuario.negocio_id, producto_id__isnull=True)
    for row in detalle_producto_negocio:
        negocioo = row.negocio_id.id
    print(negocioo)
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        form = VentaForm(request.POST)
        detalle_venta_form_set = DetalleVentaFormSet(request.POST, form_kwargs={'user': negocioo})
        if form.is_valid() and detalle_venta_form_set.is_valid():
            venta = form.save(commit=False)
            venta.save()
            detalle_venta_form_set.instance = venta
            detalle_venta_form_set.save()

            venta_stock = detalle_venta.objects.filter(venta_id=venta)
            for row in venta_stock:
                producto_stock = Producto.objects.get(id=row.producto_id.id)
                cantidad_venta = row.cantidad
                cantidad_stock = producto_stock.stock
                resta_stock = cantidad_stock - cantidad_venta
                producto_stock.stock = resta_stock
                producto_stock.save()

            return redirect('view_venta')
    else:
        form = VentaForm()
        detalle_venta_formset=DetalleVentaFormSet(form_kwargs={'user': negocioo}) # pass parameter to the form

    return render(request, 'app/venta/agregar_venta.html', {'form' : form, 'detalle_venta_formset': detalle_venta_formset } )

@login_required(login_url="/")
def eliminar_venta(request, pk):
    venta_recibida = get_object_or_404(Venta, pk=pk)
    if request.method == "POST" and request.is_ajax():
        detalle_de_venta = detalle_venta.objects.filter(venta_id=venta_recibida.id)
        for item in detalle_de_venta:
            producto_stock = Producto.objects.get(id=item.producto_id.id)
            cantidad_item = item.cantidad
            cantidad_stock = item.producto_id.stock
            suma_stock = cantidad_stock + cantidad_item
            producto_stock.stock = suma_stock
            producto_stock.save()
            item.delete()

        venta_recibida.delete()

        return HttpResponse('ok')
    else:
        dic = {
            'idd':venta_recibida.id,
            'fecha':convertir_fecha(venta_recibida.fecha),
            'total':venta_recibida.total,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')
