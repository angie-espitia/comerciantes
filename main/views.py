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
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
import datetime

def convertir_fecha(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def index(request):
    return render(request, 'pagina/index.html')

# registro de usuarios
def registrar_comerciante(request):
    error = False
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
            grupo = Group.objects.get(name="comerciante")  
            usuario.save()
            usuario.groups.add(grupo)
            usuario.save()

            myusuario = Usuario()
            myusuario.id = usuario
            myusuario.telefono = request.POST['telefono']
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

# views manejo negocio tenderos

@login_required(login_url="/")
def principal_app(request):
    return render(request, 'app/index_app.html')


@login_required(login_url="/")
def view_proveedor(request, pk):
    usuario = User.objects.get(id=pk)
    usuario_proveedor = detalle_usuario_producto.objects.filter(usuario_id=usuario.id, producto_id__isnull=True)
    return render(request, 'app/proveedor/view_proveedor.html', {'usuario_proveedor':usuario_proveedor} )

@login_required(login_url="/")
def agregar_proveedor(request, pk):

    usuario = User.objects.get(id=pk)
    usu = Usuario.objects.get(id=usuario)
    usuarioid = usuario.id
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
            usuario_proveedor = detalle_usuario_producto()
            usuario_proveedor.usuario_id = usu
            usuario_proveedor.proveedor_id = proveedor2
            usuario_proveedor.save()
            return HttpResponse('ok')

    return render(request, 'app/proveedor/agregar_proveedor.html' )

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

def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    usuario_proveedor = get_object_or_404(detalle_usuario_producto, proveedor_id=proveedor.id)
    if request.method == "POST" and request.is_ajax():
        usuario_proveedor.delete()
        proveedor.delete()

        return HttpResponse('ok')
    else:
        dic = {
            'id':proveedor.id,
            'razon_social':proveedor.razon_social,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def view_producto(request, pk):
    usuario = User.objects.get(id=pk)  
    # productos = Producto.objects.all()
    usuario_producto = detalle_usuario_producto.objects.filter(usuario_id=usuario.id, producto_id__isnull=False)
    
    return render(request, 'app/producto/view_producto.html', {'usuario_producto':usuario_producto} )

@login_required(login_url="/")
def agregar_producto(request, pk):

    usuario = User.objects.get(id=pk)
    usu = Usuario.objects.get(id=usuario)
    usuario_proveedor = detalle_usuario_producto.objects.filter(usuario_id=usuario.id, producto_id__isnull=True)
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)            
            producto.save()

            producto2 = Producto.objects.latest('id')
            proveedor_recibido = request.POST.get('usuario_proveedor')
            proveedor_p = Proveedor.objects.get(id=proveedor_recibido)

            usuario_producto = detalle_usuario_producto()
            usuario_producto.usuario_id = usu
            usuario_producto.producto_id = producto2
            usuario_producto.proveedor_id = proveedor_p
            usuario_producto.save()
            
            producto2.imagen = request.FILES.get('imagen')
            producto2.save()

            return redirect('view_producto', pk=usuario.pk)
    else:
        form = ProductoForm()

    return render(request, 'app/producto/agregar_producto.html', {'form' : form, 'usuario_proveedor': usuario_proveedor } )

@login_required(login_url="/")
def editar_producto(request, pk):
    # import pdb; pdb.set_trace()
    producto_edit = get_object_or_404(Producto, pk=pk)
    usuario = User.objects.get(id=request.user.id)    
    usuario_proveedor2 = detalle_usuario_producto.objects.filter(usuario_id=usuario.id)
    proveedor_producto = detalle_usuario_producto.objects.filter(producto_id=producto_edit.id)

    print('-------------------------------------------------')
    print(producto_edit)
    print('-------------------------------------------------')
    print(usuario)
    print('-------------------------------------------------')

    if request.method == "POST":
        form = ProductoForm_dos(request.POST, request.FILES, instance=producto_edit)
        if form.is_valid():
            producto = form.save(commit=False)            
            producto.save()

            proveedor_recibido = request.POST.get('usuario_proveedor')
            proveedor_p = Proveedor.objects.get(id=proveedor_recibido)
            proveedor_producto.proveedor_id = proveedor_p
            proveedor_producto.save()

            return HttpResponse('ok')
    else:
        form = ProductoForm_dos(instance=producto_edit)
    
    return render(request, 'app/producto/editar_producto.html', {'form' : form, 'usuario_proveedor2': usuario_proveedor2 } )

@login_required(login_url="/")
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    usuario_producto = get_object_or_404(detalle_usuario_producto, producto_id=producto.id)
    if request.method == "POST" and request.is_ajax():
        usuario_producto.delete()
        producto.delete()

        return HttpResponse('ok')
    else:
        dic = {
            'id':producto.id,
            'nombre':producto.nombre,
        }
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def view_de_compra(request):    
    return render(request, 'app/compra/view_compra.html')

@login_required(login_url="/")
def list_compras(request, pk):
    usuario = User.objects.get(id=pk)
    compra = Compra.objects.all()
    array_p = []
    for f in compra:
        array_p.append(f.id)
    detalles__compras = detalle_compra.objects.filter(compra_id__in=array_p)
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
            cantidad_stock = item_detalle_compra.producto_id.stock
            if cantidad_item > cantidad_actual:
                sum_stock = cantidad_stock + cantidad_item
                producto_stock.stock = sum_stock
                producto_stock.save()
            elif cantidad_item < cantidad_actual:
                resta_stock = cantidad_stock - cantidad_item
                producto_stock.stock = resta_stock
                producto_stock.save()

        total_item = int(item_detalle_compra.total_producto)
        if total_actual != total_item:
            compra_total =  Compra.objects.get(id=item_detalle_compra.compra_id.id)
            total_compra = compra_total.total
            if total_actual < total_item:
                sum_total = total_compra + total_item
                compra_total.total = sum_total
                compra_total.save()
            elif total_actual > total_item:
                resta_total = total_compra - total_item
                compra_total.total = resta_total
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
    usuario = User.objects.get(id=pk)
    usu = Usuario.objects.get(id=usuario)
    usuarioid = usuario.id
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        form = CompraForm(request.POST)
        detalle_compra_form_set = DetalleCompraFormSet(request.POST)
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
        detalle_compra_formset=DetalleCompraFormSet()

    return render(request, 'app/compra/agregar_compra.html', {'form' : form, 'detalle_compra_formset': detalle_compra_formset } )
