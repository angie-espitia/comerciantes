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
def view_compra(request, pk):
    usuario = User.objects.get(id=pk)
    return render(request, 'app/compra/view_compra.html')

@login_required(login_url="/")
def agregar_compra(request, pk):

    usuario = User.objects.get(id=pk)
    usu = Usuario.objects.get(id=usuario)
    usuarioid = usuario.id
    # import pdb; pdb.set_trace()
    if request.method == "POST":
        form = CompraForm(request.POST)
        if form.is_valid():
            compra = form.save(commit=False)            
            detalle_compra_form_set = DetalleCompraFormSet(request.POST)
            compra.save()
            detalle_compra_form_set.instance = compra
            detalle_compra_form_set.save()
            return redirect('view_producto', pk=usuario.pk)
    else:
        form = CompraForm()
        detalle_compra_formset=DetalleCompraFormSet()

    return render(request, 'app/compra/agregar_compra.html', {'form' : form, 'detalle_compra_formset': detalle_compra_formset } )

    # if request.method == "POST":
    #     if request.is_ajax():
    #         compra = Compra()
    #         compra.fecha = request.POST.get('fecha_compra')
    #         compra.subtotal_neto = request.POST.get('subtotal_neto_compra')
    #         compra.IVA = request.POST.get('IVA_compra')
    #         compra.total = request.POST.get('total_compra')
    #         compra.save()

    #         compra2 = Compra.objects.latest('id')
    #         proveedor_recibido = request.POST.get('usuario_proveedor')
    #         proveedor_p = Proveedor.objects.get(id=proveedor_recibido)
    #         producto_recibido = request.POST.get('usuario_producto')
    #         producto_p = Producto.objects.get(id=producto_recibido)

    #         detalle_compra = detalle_compra()
    #         detalle_compra.proveedor_id = proveedor_p
    #         detalle_compra.producto_id = producto_p
    #         detalle_compra.compra_id = compra2
    #         detalle_compra.cantidad = request.POST.get('cantidad_compra')
    #         detalle_compra.valor_unitario = request.POST.get('valor_unitario_compra')
    #         detalle_compra.total_producto = request.POST.get('total_producto_compra')
    #         detalle_compra.save()
    #         return HttpResponse('ok')

    # return render(request, 'app/compra/agregar_compra.html' )