from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.template import RequestContext
from django.contrib import messages
from main.validator import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import NoReverseMatch, reverse
from main.models import *
from main.forms import *
import json
from django.core import serializers
import datetime
import operator

def convertir_fecha(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def toJSON(self):
    return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def error_pag(request):
    return render(request, 'error.html')

def login(request):

    if request.method == 'POST':

        validators = FormLoginValidator(request.POST)

        if validators.is_valid():

            auth.login(request, validators.acceso)  # Crear una sesion
            if request.user.groups.filter(name='administrativo').exists():
                return redirect('/corporativo')
            else:
                return redirect('/usernegocios')

        else:
            return render(request, 'login.html', {'error': validators.getMessage()} )

    return render(request, 'login.html' )

@login_required(login_url="/")
def logout(request):
    auth.logout(request)
    return redirect("/")

# corporativo
@login_required(login_url="/")
def view_corporativo(request):
    # pabellon = Pabellon.objects.all()
    if request.user.groups.filter(name='administrativo').exists():
        return render(request, 'pagina/view_corporativo.html' )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def perfil_corporativo(request, pk):
    usuario = User.objects.get(id=pk)
    if request.user.groups.filter(name='administrativo').exists():
        miusuario = Usuario.objects.get(id=usuario.id)
        error = False
        if request.method == 'POST':
            # import pdb; pdb.set_trace()
            usuario.email = request.POST.get('email')
            usuario.first_name = request.POST.get('first_name')
            usuario.last_name = request.POST.get('last_name')
            usuario.save()

            miusuario.documento = request.POST.get('documento')
            miusuario.telefono = request.POST.get('telefono')
            miusuario.direccion = request.POST.get('direccion')
            miusuario.save()

            return HttpResponseRedirect(request.path_info) #redirige misma pag

        return render(request, 'pagina/perfil.html', {'usu': miusuario } )
    else:
        return render(request, 'error.html' )


# pabellones
@login_required(login_url="/")
def view_pabellon(request):
    if request.user.groups.filter(name='administrativo').exists():
        pabellon = Pabellon.objects.all()
        return render(request, 'pagina/view_pabellon.html', {'pabellon':pabellon} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def registrar_pabellon(request):
    if request.user.groups.filter(name='administrativo').exists():
        if request.method == "POST":
            form = PabellonForm(request.POST)
            if form.is_valid():
                pabellon = form.save(commit=False)
                pabellon.save()

                return redirect('view_pabellon') #, pk=usuario.pk
        else:
            form = PabellonForm()

        return render(request, 'pagina/registrar_pabellon.html', {'form' : form} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def editar_pabellon(request, pk):
    if request.user.groups.filter(name='administrativo').exists():
        pabellon = get_object_or_404(Pabellon, pk=pk)
        if request.method == "POST" and request.is_ajax():
            pabellon.nombre = request.POST.get('nombre_p')
            pabellon.descripcion = request.POST.get('descripcion_p')
            pabellon.save()
            return HttpResponse('ok')
        else:
            dic = {
                'idd':pabellon.id,
                'nombre':pabellon.nombre,
                'descripcion':pabellon.descripcion,
            }
            return HttpResponse(toJSON(dic), content_type='application/json')
    else:
        return render(request, 'error.html' )

# registro de propietario y empresa
@login_required(login_url="/")
def view_comerciantes(request):
    if request.user.groups.filter(name='administrativo').exists():
        usuarios = User.objects.filter(groups__name='propietario_negocio')
        propietario_negocios = Usuario.objects.filter(id__in=usuarios)
        print(propietario_negocios)
        return render(request, 'pagina/view_propietarios.html', {'propietario_negocios':propietario_negocios} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def registrar_comerciante(request):
    if request.user.groups.filter(name='administrativo').exists():
        error = False
        if request.method == 'POST':
            validators = FormRegistroValidator(request.POST)
            validators.required = ['nombre', 'apellido', 'email', 'username', 'password1']

            if validators.is_valid():
                try:
                    usuario = User()
                    usuario.first_name = request.POST['nombre']
                    usuario.last_name = request.POST['apellido']
                    usuario.email = request.POST['email']
                    usuario.username = request.POST['username']
                    usuario.password = make_password(request.POST['password1'])
                    usuario.is_active = True
                    grupo = Group.objects.get(name="propietario_negocio")
                    usuario.save()
                    usuario.groups.add(grupo)
                    usuario.save()

                    myusuario = Usuario()
                    myusuario.id = usuario
                    myusuario.documento = request.POST['documento']
                    myusuario.save()

                    return redirect('view_comerciantes')
                except Exception as e:
                    messages.error(request, 'El usuario no es valido, por favor eliga otro usuario.')
            else:
                messages.error(request, validators.getMessage() )
            # Agregar el usuario a la base de datos
        return render( request, 'pagina/registrar_tendero.html' )
    else:
        return render(request, 'error.html' )

# pabellones
@login_required(login_url="/")
def view_negocio(request):
    if request.user.groups.filter(name='administrativo').exists():
        propietario_negocio = User.objects.filter(groups__name='propietario_negocio')
        usuario = Usuario.objects.filter(id__in=propietario_negocio)
        usuario_negocio = detalle_usuario_negocio.objects.filter(usuario_id__in=usuario)
        return render(request, 'pagina/view_negocios.html', {'usuario_negocio':usuario_negocio} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def registrar_negocio(request):
    if request.user.groups.filter(name='administrativo').exists():
        pabellon = Pabellon.objects.all()
        propietario_negocio = User.objects.filter(groups__name='propietario_negocio')
        # import pdb; pdb.set_trace()
        if request.method == 'POST':
            form = NegocioForm(request.POST)
            if form.is_valid():
                negocio = form.save(commit=False)

                usuario_recibido = request.POST.get('usuario_id')
                pabellon_recibido = request.POST.get('pabellon_id')
                usuario_p = Usuario.objects.get(id=usuario_recibido)
                pabellon_p = Pabellon.objects.get(id=pabellon_recibido)
                negocio.pabellon_id = pabellon_p
                negocio.save()

                negocio2 = Negocio.objects.latest('id')
                negocio_usuario = detalle_usuario_negocio()
                negocio_usuario.negocio_id = negocio2
                negocio_usuario.usuario_id = usuario_p
                negocio_usuario.save()

                return redirect('view_negocio')

        else:
            form = NegocioForm()

        return render(request, 'pagina/registrar_negocio.html', {'form' : form, 'propietario_negocio' : propietario_negocio, 'pabellon' : pabellon} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def editar_negocio(request, pk):
    if request.user.groups.filter(name='administrativo').exists():
        negocio_recibido = get_object_or_404(Negocio, pk=pk)
        pabellon = Pabellon.objects.all()
        propietario_negocio = User.objects.filter(groups__name='propietario_negocio')
        usuario_negocio = detalle_usuario_negocio.objects.filter(negocio_id=negocio_recibido).first()
        print(usuario_negocio)

        if request.method == "POST":
            form = NegocioForm_dos(request.POST, instance=negocio_recibido)
            form2 = DetalleUsuarioNegocioForm(request.POST, instance=usuario_negocio)
            if form.is_valid():
                negocio = form.save(commit=False)
                negocio.save()
                negocio_usuario = form2.save(commit=False)
                negocio_usuario.save()

                return redirect('view_negocio') #redirige misma pag
        else:
            form = NegocioForm_dos(instance=negocio_recibido)
            form2 = DetalleUsuarioNegocioForm(instance=usuario_negocio)
        return render(request, 'pagina/detalle_negocio.html', {'form' : form, 'form2':form2, 'propietario_negocio' : propietario_negocio, 'pabellon' : pabellon} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def eliminar_negocio(request, pk):
    if request.user.groups.filter(name='administrativo').exists():
        negocio = get_object_or_404(Negocio, pk=pk)
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=True)
        negocio_usuario = detalle_usuario_negocio.objects.filter(negocio_id=negocio.id)
        count_n = 0
        for x in negocio_usuario:
            count_n += 1

        print(count_n)
        if request.method == "POST" and request.is_ajax():
            if not negocio_producto and count_n < 2:
                negocio_usuario.delete()
                negocio.delete()
                return HttpResponse('1')
            else:
                return HttpResponse('2')
        else:
            dic = {
                'id':negocio.id,
                'nombre':negocio.nombre,
            }
            return HttpResponse(toJSON(dic), content_type='application/json')
    else:
        return render(request, 'error.html' )

# ------------------------------- views manejo negocio tenderos ---------------------------------------------------------

@login_required(login_url="/")
def escojer_negocio(request):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio_usuario = detalle_usuario_negocio.objects.filter(usuario_id=usuario)
    arr_n = []
    for x in negocio_usuario:
        n = x.negocio_id.id
        arr_n.append(n)

    negocio = Negocio.objects.filter(id__in=arr_n)

    return render(request, 'escojer.html', {'negocio':negocio})

@login_required(login_url="/")
def principal_app(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
        # producto de poco stock
        negocioo = []
        for x in negocio_producto:
            if x.producto_id.stock <= 14 and x.producto_id.estado=='1':
                negocioo.append(x)

        array_producto = []
        array_producto_name = []
        for f in negocio_producto:
            array_producto.append(f.producto_id.id)
            array_producto_name.append(f.producto_id.nombre)

        venta = Venta.objects.all()
        array_venta = []
        for f in venta:
            array_venta.append(f.id)
        detalles__ventas = detalle_venta.objects.filter(venta_id__in=array_venta, producto_id__in=array_producto)

        dic_arr = {} # diccionario de productos totales
        for i in array_producto_name:
            dic_arr.update({ i: [] })

        for x in detalles__ventas: # for para guardar la cantidad de productos vendidos individuales
            for i in dic_arr:
                if x.producto_id.nombre == i:
                    dic_arr[i].append(x.cantidad)

        dic_result = {}
        for key, value in dic_arr.items(): # iterar los item del diccionario
            suma = 0 # variable donde se guardará la suma de los elementos
            for v in value: # iterar los elementos
                suma += v # sumar los elementos y guardarlos
            dic_result[key] = suma # añadir al nuevo diccionario la misma llave con la suma de los elementos

        resultado = sorted(dic_result.items(), key=operator.itemgetter(1))
        resultado.reverse()

        return render( request, 'app/index_app.html', {'negocioo':negocioo, 'detalles__ventas': detalles__ventas, 'negocio_id': negocio, 'resultado': resultado } )
    else:
        return render(request, 'error.html' )

# registro de empleados
@login_required(login_url="/")
def registrar_empleado(request, pk):
    error = False
    usuario = Usuario.objects.get(id=request.user.id)
    negocio_actual = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio_actual.id, usuario_id=usuario).exists():
        us = Usuario.objects.all()
        if request.method == 'POST':
            validators = FormRegistroValidator(request.POST)
            validators.required = ['nombre', 'apellido', 'email', 'username', 'password1']

            if validators.is_valid():
                try:
                    usuario = User()
                    usuario.first_name = request.POST['nombre']
                    usuario.last_name = request.POST['apellido']
                    usuario.email = request.POST['email']
                    usuario.username = request.POST['username']
                    usuario.password = make_password(request.POST['password1'])
                    usuario.is_active = True
                    grupo = Group.objects.get(name="empleado_negocio")
                    usuario.save()
                    usuario.groups.add(grupo)
                    usuario.save()

                    myusuario = Usuario()
                    myusuario.id = usuario
                    myusuario.documento = request.POST['documento']
                    myusuario.telefono = request.POST['telefono']

                    myusuario.save()
                    negocio_usuario = detalle_usuario_negocio()
                    negocio_usuario.usuario_id = myusuario
                    negocio_usuario.negocio_id = negocio_actual
                    negocio_usuario.save()

                    return redirect('list_usuarios', pk=negocio_actual.pk)

                except Exception as e:
                    messages.error(request, 'El usuario no es valido, por favor eliga otro usuario.')

            else:
                messages.error(request, validators.getMessage() )
            # Agregar el usuario a la base de datos
        return render( request, 'app/administracion/registrar_empleado.html', {'negocio_id': negocio_actual, 'us':us} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def perfil_usuario(request, pk):
    negocio_actual = Negocio.objects.get(id=pk)
    usuario = User.objects.get(id=request.user.id)
    miusuario = Usuario.objects.get(id=usuario.id)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio_actual.id, usuario_id=miusuario).exists():
        error = False
        if request.method == 'POST':
            # import pdb; pdb.set_trace()
            usuario.email = request.POST.get('email')
            usuario.first_name = request.POST.get('first_name')
            usuario.last_name = request.POST.get('last_name')
            usuario.save()

            miusuario.documento = request.POST.get('documento')
            miusuario.telefono = request.POST.get('telefono')
            miusuario.direccion = request.POST.get('direccion')
            miusuario.save()

            return HttpResponseRedirect(request.path_info) #redirige misma pag

        return render(request, 'app/administracion/perfil_usuario.html', {'usu': miusuario, 'negocio_id': negocio_actual } )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def list_usuarios(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        lista_usuarios = detalle_usuario_negocio.objects.filter(negocio_id=negocio)
        for x in lista_usuarios:
            print(x)
        return render(request, 'app/administracion/lista_usuarios.html', {'usuarioss':lista_usuarios,'negocio_id': negocio})
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def modificar_contra(request, pk):
    error = False
    negocio_actual = Negocio.objects.get(id=pk)
    usuario_contra = User.objects.get(id=request.user.id)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio_actual.id, usuario_id=usuario_contra.id).exists():
        if request.method == 'POST':
            usuario_contra.password = make_password(request.POST['password1'])
            usuario_contra.save()
            # log(request, "CONTRASEÑA_MODIFICADA")
            return HttpResponseRedirect(request.path_info) #redirige misma pag
    else:
        return render(request, 'error.html' )

# proveedor
@login_required(login_url="/")
def view_proveedor(request, pk):
    negocio_actual = Negocio.objects.get(id=pk)
    usuario = Usuario.objects.get(id=request.user.id)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio_actual.id, usuario_id=usuario).exists():
        negocio_proveedor = detalle_negocio_producto.objects.filter(negocio_id=negocio_actual.id, producto_id__isnull=True)

        return render(request, 'app/proveedor/view_proveedor.html', {'negocio_proveedor':negocio_proveedor, 'negocio_id': negocio_actual} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def agregar_proveedor(request, pk):
    usu = Usuario.objects.get(id=request.user.id)
    negocioo = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocioo.id, usuario_id=usu).exists():
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
                negocio_proveedor.negocio_id = negocioo
                negocio_proveedor.proveedor_id = proveedor2
                negocio_proveedor.save()
                return HttpResponse('ok')

        return render(request, 'app/proveedor/agregar_proveedor.html', {'negocio_id': negocioo} )
    else:
        return render(request, 'error.html' )

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
        return HttpResponse(toJSON(dic), content_type='application/json')

# producto
@login_required(login_url="/")
def view_producto(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)

        return render(request, 'app/producto/view_producto.html', {'negocio_producto':negocio_producto, 'negocio_id': negocio} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def agregar_producto(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_proveedor = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=True)
        # import pdb; pdb.set_trace()

        if request.method == "POST":
            form = ProductoForm(request.POST, request.FILES)
            if form.is_valid():
                producto = form.save(commit=False)
                producto.estado = '1'
                producto.save()

                producto2 = Producto.objects.latest('id')
                proveedor_recibido = request.POST.get('negocio_proveedor')
                proveedor_p = Proveedor.objects.get(id=proveedor_recibido)

                negocio_producto = detalle_negocio_producto()
                negocio_producto.negocio_id = negocio
                negocio_producto.producto_id = producto2
                negocio_producto.proveedor_id = proveedor_p
                negocio_producto.save()

                producto2.imagen = request.FILES.get('imagen')
                producto2.save()

                return redirect('view_producto', pk=negocio.pk)
        else:
            form = ProductoForm()

        return render(request, 'app/producto/agregar_producto.html', {'form' : form, 'negocio_proveedor': negocio_proveedor,'negocio_id': negocio} )
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def detalle_producto(request, pk):
    producto_recibido = get_object_or_404(Producto, pk=pk)
    detalle_producto_negocio = detalle_negocio_producto.objects.filter(producto_id=producto_recibido.id)
    for x in detalle_producto_negocio:
        id_c = x

    for row in detalle_producto_negocio:
        d_p_u = get_object_or_404(detalle_negocio_producto, pk=row.id)
        negocioo = d_p_u.negocio_id
    detalle_compra_producto = detalle_compra.objects.filter(producto_id=producto_recibido.id)

    if request.method == "POST":
        form = ProductoForm_dos(request.POST, request.FILES, instance=producto_recibido)
        form2 = DetalleNegocioProductoForm(request.POST, instance=id_c,user=negocioo.id, producto=producto_recibido)
        if form.is_valid() and form2.is_valid():
            producto = form.save(commit=False)
            producto.save()
            producto2 = form2.save(commit=False)
            producto2.save()

            return HttpResponseRedirect(request.path_info, {'negocio_id': negocioo}) #redirige misma pag
    else:
        form = ProductoForm_dos(instance=producto_recibido)
        form2 = DetalleNegocioProductoForm(instance=id_c,user=negocioo.id,producto=producto_recibido)
    return render(request, 'app/producto/editar_producto.html', {'detalle_producto_negocio':detalle_producto_negocio, 'detalle_compra_producto':detalle_compra_producto, 'form' : form, 'form2':form2, 'negocio_id': negocioo} )

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
        return HttpResponse(toJSON(dic), content_type='application/json')

# compras
@login_required(login_url="/")
def view_de_compra(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        return render(request, 'app/compra/view_compra.html',{'negocio_id': negocio})
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def view_de_reportes_compra(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        return render(request, 'app/compra/view_reportes_compra.html',{'negocio_id': negocio})
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def list_compras(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_proveedor = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=True)
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

        # valores_ord = dict(sorted(dic.items(), reverse=True)) # reverse valores
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def list_compras_reportes(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
        array_producto = []
        for f in negocio_producto:
            array_producto.append(f.producto_id.id)
        compra = Compra.objects.all()
        array_compra = []
        for f in compra:
            array_compra.append(f.id)
        detalles__compras = detalle_compra.objects.filter(compra_id__in=array_compra, producto_id__in=array_producto)
        dic = {}
        va = 1
        for i in detalles__compras:
                dic[va] = {
                    'id_compra':i.compra_id.id,
                    'fecha':convertir_fecha(i.compra_id.fecha),
                    'total':i.compra_id.total,
                    'proveedor':i.proveedor_id.razon_social,
                    'producto_id':i.producto_id.id,
                    'producto_nombre':i.producto_id.nombre,
                    'producto_stock_nuevo':i.cantidad_stock_momento,
                    'producto_cantidad':i.cantidad,
                    'valor_unitario':i.valor_unitario,
                    'producto_total':i.total_producto,
                    'producto_stock_anterior':i.cantidad_stock_anterior,
                }
                va += 1

        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def view_de_reportes_gastos(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        return render(request, 'app/compra/view_reporte_gastos.html',{'negocio_id': negocio})
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def list_compras_reportes_gastos(request, pk):
    now = datetime.datetime.now()
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
        array_producto = []
        for f in negocio_producto:
            array_producto.append(f.producto_id.id)
        compra = Compra.objects.all()
        array_compra = []
        for f in compra:
            array_compra.append(f.id)
        detalles__compras = detalle_compra.objects.filter(compra_id__in=array_compra, producto_id__in=array_producto) # compras por negocio y productos

        #funcion para guardar total compras por mes de anio actual
        dic_mes = { '01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]} # diccionario de ventas mes anio actual totales
        anio_actual = now.year # anio actual
        for f in detalles__compras:
            x = convertir_fecha(f.compra_id.fecha)
            if str(x.split('-')[0]) == str(anio_actual):
                for key in dic_mes:
                    if key == str(x.split('-')[1]):
                        dic_mes[key].append(f.total_producto)

        dic_meses_anio_actual = {}
        for key, value in dic_mes.items(): # iterar los item del diccionario
            suma = 0 # variable donde se guardará la suma de los elementos
            for v in value: # iterar los elementos
                suma += v # sumar los elementos y guardarlos
            dic_meses_anio_actual[key] = suma # añadir al nuevo diccionario la misma llave con la suma de los elementos

        # funcion para guardar totalcompras por dia de todos los meses del anio actal
        dic_mes_dia = {'01':{},'02':{},'03':{},'04':{},'05':{},'06':{},'07':{},'08':{},'09':{},'10':{},'11':{},'12':{}} # dic inicial
        dic_meses_dia_anio_actual = {'01':{},'02':{},'03':{},'04':{},'05':{},'06':{},'07':{},'08':{},'09':{},'10':{},'11':{},'12':{}} #dic final
        for f in detalles__compras: # agrega diccionario dias a las llaves de meses
            w = convertir_fecha(f.compra_id.fecha)
            x = w.split(' ')[0]
            if str(x.split('-')[0]) == str(anio_actual):
                dic_mes_dia[x.split('-')[1]].update({ x.split('-')[2] : [] })
                dic_meses_dia_anio_actual[x.split('-')[1]].update({ x.split('-')[2] : [] })

        for ff in detalles__compras: #agrega los totales de compras por dias del mes
             w = convertir_fecha(ff.compra_id.fecha)
             x = w.split(' ')[0]
             if str(x.split('-')[0]) == str(anio_actual):
                 for key in dic_mes_dia:
                     if key == str(x.split('-')[1]):
                         for key2 in dic_mes_dia[key]:
                             if key2 == str(x.split('-')[2]):
                                 dic_mes_dia[key][key2].append(ff.total_producto)

        for llave in dic_mes_dia: #suma los totales de compras por dia del mes
            for key, value in dic_mes_dia[llave].items():
                suma = 0
                for v in value:
                    suma += v
                dic_meses_dia_anio_actual[llave][key] = suma

        # funcion para guardar total compras por proveedor proveedor dia de todos los meses del anio actal
        dic_mes_dia_prov = {'01':{},'02':{},'03':{},'04':{},'05':{},'06':{},'07':{},'08':{},'09':{},'10':{},'11':{},'12':{}} # dic inicial
        dic_meses_dia_anio_actual_prov = {'01':{},'02':{},'03':{},'04':{},'05':{},'06':{},'07':{},'08':{},'09':{},'10':{},'11':{},'12':{}} #dic final
        for f in detalles__compras: # agrega diccionario dias a las llaves de meses
            w = convertir_fecha(f.compra_id.fecha)
            x = w.split(' ')[0]
            if str(x.split('-')[0]) == str(anio_actual):
                dic_mes_dia_prov[x.split('-')[1]].update({ x.split('-')[2] : {} })
                dic_meses_dia_anio_actual_prov[x.split('-')[1]].update({ x.split('-')[2] : {} })

        for ff in detalles__compras: # agrega diccionario proveedores a las llaves dias a las llaves de meses
            w = convertir_fecha(ff.compra_id.fecha)
            x = w.split(' ')[0]
            if str(x.split('-')[0]) == str(anio_actual):
                for dia in dic_mes_dia_prov[x.split('-')[1]]:
                    dic_mes_dia_prov[x.split('-')[1]][dia].update({ ff.proveedor_id.razon_social : [] })
                    dic_meses_dia_anio_actual_prov[x.split('-')[1]][dia].update({ ff.proveedor_id.razon_social : [] })

        for fff in detalles__compras: #agrega los totales de compras por dias del mes
            w = convertir_fecha(fff.compra_id.fecha)
            x = w.split(' ')[0]
            if str(x.split('-')[0]) == str(anio_actual):
                for key in dic_mes_dia_prov:
                    if key == str(x.split('-')[1]):
                        for dia in dic_mes_dia_prov[key]:
                            if dia == str(x.split('-')[2]):
                                for prov in dic_mes_dia_prov[key][dia]:
                                    if prov == str(fff.proveedor_id.razon_social):
                                        dic_mes_dia_prov[key][dia][prov].append(fff.total_producto)

        for mes in dic_mes_dia_prov: #suma los totales de compras por dia del mes
            for dia in dic_mes_dia_prov[mes]:
                for prov, value in dic_mes_dia_prov[mes][dia].items():
                    suma = 0
                    for v in value:
                        suma += v
                    dic_meses_dia_anio_actual_prov[mes][dia][prov] = suma

        # funcion total compras por mes y anio
        dic_anio_mes = {}
        dic_anio_meses_estesi = {}
        for f in detalles__compras: # guarda llave anios
            w = convertir_fecha(f.compra_id.fecha)
            x = w.split(' ')[0]
            dic_anio_mes.update({x.split('-')[0]:{}})
            dic_anio_meses_estesi.update({x.split('-')[0]:{}})

        for ff in detalles__compras: # guarda mes anios
            w = convertir_fecha(ff.compra_id.fecha)
            x = w.split(' ')[0]
            for key in dic_anio_mes:
                if str(x.split('-')[0]) == key:
                    dic_anio_mes[key].update({ x.split('-')[1] : [] })
                    dic_anio_meses_estesi[key].update({ x.split('-')[1] : [] })

        for fff in detalles__compras: #agrega los totales de compras por mes del anio
             w = convertir_fecha(fff.compra_id.fecha)
             x = w.split(' ')[0]
             for key in dic_anio_mes:
                 if key == str(x.split('-')[0]): # anio
                     for key2 in dic_anio_mes[key]:
                         if key2 == str(x.split('-')[1]): # mes
                             dic_anio_mes[key][key2].append(fff.total_producto)

        for llave in dic_anio_mes: #suma los totales de compras mes de anios
            for key, value in dic_anio_mes[llave].items():
                suma = 0
                for v in value:
                    suma += v
                dic_anio_meses_estesi[llave][key] = suma

        # dic_meses_anio_actual = diccionario con el total por meses del anio vigente
        # dic_meses_dia_anio_actual_prov = diccionario con total por proveedor por dia de todos los meses del anio vigente
        # dic_meses_dia_anio_actual = diccionario con el total por dia de todos los meses del anio vigente
        # dic_anio_meses_estesi = diccionario con los totales de venta por meses de cada anio registrado

        dic_final = {'mes_anio_actual':{},'dia_mes_anio_actual':{},'dia_mes_prov_anio_actual':{},'meses_anios':{}}
        dic_final['mes_anio_actual'].update(dic_meses_anio_actual)
        dic_final['dia_mes_anio_actual'].update(dic_meses_dia_anio_actual)
        dic_final['dia_mes_prov_anio_actual'].update(dic_meses_dia_anio_actual_prov)
        dic_final['meses_anios'].update(dic_anio_meses_estesi)

        return HttpResponse(toJSON(dic_final), content_type='application/json')
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def detalle_de_compra(request, pk):
    detalles__compras = detalle_compra.objects.filter(compra_id=pk)
    compra = Compra.objects.filter(id=pk)
    for x in detalles__compras:
        proveedor = x.proveedor_id
        print(proveedor)
    negocio_proveedor = detalle_negocio_producto.objects.filter(proveedor_id=proveedor.id, producto_id__isnull=True)
    for x in negocio_proveedor:
        negocio_id = x.negocio_id
        print(negocio_id)

    return render(request, 'app/compra/detalle_compra.html', {'detalles__compras' : detalles__compras, 'compra' : compra, 'negocio_id': negocio_id })

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
            item_detalle_compra.cantidad_stock_momento = sum_stock
            item_detalle_compra.save()

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
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def agregar_compra(request, pk):
    try:
        # import pdb; pdb.set_trace()
        usuario = Usuario.objects.get(id=request.user.id)
        negocio = Negocio.objects.get(id=pk)
        if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
            detalle_producto_negocio = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=True)

            for row in detalle_producto_negocio:
                negocioo = row.negocio_id.id

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

                        row.cantidad_stock_anterior = cantidad_stock
                        row.save()

                        sum_stock = cantidad_compra + cantidad_stock
                        producto_stock.stock = sum_stock
                        row.cantidad_stock_momento = sum_stock
                        row.save()
                        producto_stock.save()

                    return redirect('view_compra', pk=negocio.pk)
            else:
                form = CompraForm()
                detalle_compra_formset=DetalleCompraFormSet(form_kwargs={'user': negocioo}) # pass parameter to the form

            return render(request, 'app/compra/agregar_compra.html', {'form' : form, 'detalle_compra_formset': detalle_compra_formset, 'negocio_id': negocio, 'proveedores':detalle_producto_negocio } )
        else:
            return render(request, 'error.html' )
    except:
        return render(request, 'app/error.html', {'negocio_id': negocio} )

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
        return HttpResponse(toJSON(dic), content_type='application/json')

# venta
@login_required(login_url="/")
def view_de_venta(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        return render(request, 'app/venta/view_venta.html',{'negocio_id': negocio})
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def view_de_reportes_venta(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        return render(request, 'app/venta/view_reportes_venta.html',{'negocio_id': negocio})
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def list_ventas(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
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
        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def list_ventas_reportes(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
        array_producto = []
        for f in negocio_producto:
            array_producto.append(f.producto_id.id)
        venta = Venta.objects.all()
        array_venta = []
        for f in venta:
            array_venta.append(f.id)
        detalles__ventas = detalle_venta.objects.filter(venta_id__in=array_venta, producto_id__in=array_producto)
        dic = {}
        va = 1
        for i in detalles__ventas:
                dic[va] = {
                    'id_venta':i.venta_id.id,
                    'fecha':convertir_fecha(i.venta_id.fecha),
                    'total':i.venta_id.total,
                    'producto_id':i.producto_id.id,
                    'producto_nombre':i.producto_id.nombre,
                    'producto_stock_nuevo':i.cantidad_stock_momento,
                    'producto_cantidad':i.cantidad,
                    'producto_total':i.total_producto,
                    'producto_stock_anterior':i.cantidad_stock_anterior,
                }
                va += 1

        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def view_de_reportes_ganancias(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        return render(request, 'app/venta/view_reporte_ganancias.html',{'negocio_id': negocio})
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def list_ventas_reportes_ganancias(request, pk):
    now = datetime.datetime.now()
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
        array_producto = []
        for f in negocio_producto:
            array_producto.append(f.producto_id.id)
        venta = Venta.objects.all()
        array_venta = []
        for f in venta:
            array_venta.append(f.id)
        detalles__ventas = detalle_venta.objects.filter(venta_id__in=array_venta, producto_id__in=array_producto) # ventas por negocio y productos

        #funcion para guardar total ventas por mes de anio actual
        dic_mes = { '01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]} # diccionario de ventas mes anio actual totales
        anio_actual = now.year # anio actual
        for f in detalles__ventas:
            x = convertir_fecha(f.venta_id.fecha)
            if str(x.split('-')[0]) == str(anio_actual):
                for key in dic_mes:
                    if key == str(x.split('-')[1]):
                        dic_mes[key].append(f.total_producto)

        dic_meses_anio_actual = {}
        for key, value in dic_mes.items(): # iterar los item del diccionario
            suma = 0 # variable donde se guardará la suma de los elementos
            for v in value: # iterar los elementos
                suma += v # sumar los elementos y guardarlos
            dic_meses_anio_actual[key] = suma # añadir al nuevo diccionario la misma llave con la suma de los elementos

        # funcion para guardar total ventas por dia de todos los meses del anio actal
        dic_mes_dia = {'01':{},'02':{},'03':{},'04':{},'05':{},'06':{},'07':{},'08':{},'09':{},'10':{},'11':{},'12':{}} # dic inicial
        dic_meses_dia_anio_actual = {'01':{},'02':{},'03':{},'04':{},'05':{},'06':{},'07':{},'08':{},'09':{},'10':{},'11':{},'12':{}} #dic final
        for f in detalles__ventas: # agrega diccionario dias a las llaves de meses
            w = convertir_fecha(f.venta_id.fecha)
            x = w.split(' ')[0]
            if str(x.split('-')[0]) == str(anio_actual):
                dic_mes_dia[x.split('-')[1]].update({ x.split('-')[2] : [] })
                dic_meses_dia_anio_actual[x.split('-')[1]].update({ x.split('-')[2] : [] })

        for ff in detalles__ventas: #agrega los totales de ventas por dias del mes
             w = convertir_fecha(ff.venta_id.fecha)
             x = w.split(' ')[0]
             if str(x.split('-')[0]) == str(anio_actual):
                 for key in dic_mes_dia:
                     if key == str(x.split('-')[1]):
                         for key2 in dic_mes_dia[key]:
                             if key2 == str(x.split('-')[2]):
                                 dic_mes_dia[key][key2].append(ff.total_producto)

        for llave in dic_mes_dia: #suma los totales de ventas por dia del mes
            for key, value in dic_mes_dia[llave].items():
                suma = 0
                for v in value:
                    suma += v
                dic_meses_dia_anio_actual[llave][key] = suma

        # funcion total ventas por mes y anio
        dic_anio_mes = {}
        dic_anio_meses_estesi = {}
        for f in detalles__ventas: # guarda llave anios
            w = convertir_fecha(f.venta_id.fecha)
            x = w.split(' ')[0]
            dic_anio_mes.update({x.split('-')[0]:{}})
            dic_anio_meses_estesi.update({x.split('-')[0]:{}})

        for ff in detalles__ventas: # guarda mes anios
            w = convertir_fecha(ff.venta_id.fecha)
            x = w.split(' ')[0]
            for key in dic_anio_mes:
                if str(x.split('-')[0]) == key:
                    dic_anio_mes[key].update({ x.split('-')[1] : [] })
                    dic_anio_meses_estesi[key].update({ x.split('-')[1] : [] })

        for fff in detalles__ventas: #agrega los totales de ventas por mes del anio
             w = convertir_fecha(fff.venta_id.fecha)
             x = w.split(' ')[0]
             for key in dic_anio_mes:
                 if key == str(x.split('-')[0]): # anio
                     for key2 in dic_anio_mes[key]:
                         if key2 == str(x.split('-')[1]): # mes
                             dic_anio_mes[key][key2].append(fff.total_producto)

        for llave in dic_anio_mes: #suma los totales de ventas mes de anios
            for key, value in dic_anio_mes[llave].items():
                suma = 0
                for v in value:
                    suma += v
                dic_anio_meses_estesi[llave][key] = suma

        # dic_meses_anio_actual = diccionario con el total por meses del anio vigente
        # dic_meses_dia_anio_actual = diccionario con el total por dia de todos los meses del anio vigente
        # dic_anio_meses_estesi = diccionario con los totales de venta por meses de cada anio registrado

        dic_final = {'mes_anio_actual':{},'dia_mes_anio_actual':{},'meses_anios':{}}
        dic_final['mes_anio_actual'].update(dic_meses_anio_actual)
        dic_final['dia_mes_anio_actual'].update(dic_meses_dia_anio_actual)
        dic_final['meses_anios'].update(dic_anio_meses_estesi)

        return HttpResponse(toJSON(dic_final), content_type='application/json')
    else:
        return render(request, 'error.html' )

@login_required(login_url="/")
def detalle_de_venta(request, pk):
    detalles__ventas = detalle_venta.objects.filter(venta_id=pk)
    venta = Venta.objects.filter(id=pk)
    for x in detalles__ventas:
        producto = x.producto_id
        print(producto)
    negocio_producto = detalle_negocio_producto.objects.filter(producto_id=producto.id)
    for x in negocio_producto:
        negocio_id = x.negocio_id
        print(negocio_id)
    return render(request, 'app/venta/detalle_venta.html', {'detalles__ventas' : detalles__ventas, 'venta' : venta, 'negocio_id': negocio_id })

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
            item_detalle_venta.cantidad_stock_momento = resta_stock
            item_detalle_venta.save()

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
        return HttpResponse(toJSON(dic), content_type='application/json')

@login_required(login_url="/")
def agregar_venta(request, pk):
    try:
        usuario = Usuario.objects.get(id=request.user.id)
        negocio = Negocio.objects.get(id=pk)
        if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
            detalle_producto_negocio = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=True)
            for row in detalle_producto_negocio:
                negocioo = row.negocio_id.id

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

                        row.cantidad_stock_anterior = cantidad_stock
                        row.save()

                        resta_stock = cantidad_stock - cantidad_venta
                        producto_stock.stock = resta_stock
                        row.cantidad_stock_momento = resta_stock
                        row.save()
                        producto_stock.save()

                    return redirect('view_venta', pk=negocio.pk)
            else:
                form = VentaForm()
                detalle_venta_formset=DetalleVentaFormSet(form_kwargs={'user': negocioo}) # pass parameter to the form

            return render(request, 'app/venta/agregar_venta.html', {'form' : form, 'detalle_venta_formset': detalle_venta_formset, 'negocio_id': negocio } )
        else:
            return render(request, 'error.html' )
    except:
        return render(request, 'app/error.html', {'negocio_id': negocio} )

@login_required(login_url="/")
def datos_agregar_venta(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    if detalle_usuario_negocio.objects.filter(negocio_id=negocio.id, usuario_id=usuario).exists():
        detalle_producto_negocio = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
        dic = {}
        for x in detalle_producto_negocio:
            dic[x.producto_id.id]=[x.producto_id.id,x.producto_id.nombre,x.producto_id.stock]

        print(dic)
        return HttpResponse(toJSON(dic), content_type='application/json')
    else:
        return render(request, 'error.html' )

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
        return HttpResponse(toJSON(dic), content_type='application/json')
