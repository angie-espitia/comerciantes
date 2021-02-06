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

# def index(request):
#     return render(request, 'login.html')

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
    print(request.user)
    return render(request, 'pagina/view_corporativo.html' )

@login_required(login_url="/")
def perfil_corporativo(request, pk):
    usuario = User.objects.get(id=pk)
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


# pabellones
@login_required(login_url="/")
def view_pabellon(request):
    pabellon = Pabellon.objects.all()
    return render(request, 'pagina/view_pabellon.html', {'pabellon':pabellon} )

@login_required(login_url="/")
def registrar_pabellon(request):
    if request.method == "POST":
        form = PabellonForm(request.POST)
        if form.is_valid():
            pabellon = form.save(commit=False)
            pabellon.save()

            return redirect('view_pabellon') #, pk=usuario.pk
    else:
        form = PabellonForm()

    return render(request, 'pagina/registrar_pabellon.html', {'form' : form} )

@login_required(login_url="/")
def editar_pabellon(request, pk):
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

# registro de propietario y empresa
@login_required(login_url="/")
def view_comerciantes(request):
    usuarios = User.objects.filter(groups__name='propietario_negocio')
    propietario_negocios = Usuario.objects.filter(id__in=usuarios)
    print(propietario_negocios)
    return render(request, 'pagina/view_propietarios.html', {'propietario_negocios':propietario_negocios} )

@login_required(login_url="/")
def registrar_comerciante(request):
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

# pabellones
@login_required(login_url="/")
def view_negocio(request):
    propietario_negocio = User.objects.filter(groups__name='propietario_negocio')
    usuario = Usuario.objects.filter(id__in=propietario_negocio)
    usuario_negocio = detalle_usuario_negocio.objects.filter(usuario_id__in=usuario)
    return render(request, 'pagina/view_negocios.html', {'usuario_negocio':usuario_negocio} )

@login_required(login_url="/")
def registrar_negocio(request):
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

@login_required(login_url="/")
def editar_negocio(request, pk):
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

@login_required(login_url="/")
def eliminar_negocio(request, pk):
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
    negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
    # producto de poco stock
    negocioo = []
    for x in negocio_producto:
        if x.producto_id.stock <= 9 and x.producto_id.estado=='1':
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
    print(resultado)

    return render( request, 'app/index_app.html', {'negocioo':negocioo, 'detalles__ventas': detalles__ventas, 'negocio_id': negocio, 'resultado': resultado } )

# registro de empleados
@login_required(login_url="/")
def registrar_empleado(request, pk):
    error = False
    usuario = Usuario.objects.get(id=request.user.id)
    negocio_actual = Negocio.objects.get(id=pk)
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

@login_required(login_url="/")
def perfil_usuario(request, pk):
    negocio_actual = Negocio.objects.get(id=pk)
    usuario = User.objects.get(id=request.user.id)
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

    return render(request, 'app/administracion/perfil_usuario.html', {'usu': miusuario, 'negocio_id': negocio_actual } )

@login_required(login_url="/")
def list_usuarios(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    print(negocio)
    lista_usuarios = detalle_usuario_negocio.objects.filter(negocio_id=negocio)
    for x in lista_usuarios:
        print(x)
    return render(request, 'app/administracion/lista_usuarios.html', {'usuarioss':lista_usuarios,'negocio_id': negocio})

@login_required(login_url="/")
def modificar_contra(request, pk):
    error = False
    # negocio_actual = Negocio.objects.get(id=pk)
    usuario_contra = User.objects.get(id=request.user.id)
    if request.method == 'POST':
        usuario_contra.password = make_password(request.POST['password1'])
        usuario_contra.save()
        # log(request, "CONTRASEÑA_MODIFICADA")
        return HttpResponseRedirect(request.path_info) #redirige misma pag

# proveedor
@login_required(login_url="/")
def view_proveedor(request, pk):
    negocio_actual = Negocio.objects.get(id=pk)
    usuario = Usuario.objects.get(id=request.user.id)
    negocio_proveedor = detalle_negocio_producto.objects.filter(negocio_id=negocio_actual.id, producto_id__isnull=True)

    return render(request, 'app/proveedor/view_proveedor.html', {'negocio_proveedor':negocio_proveedor, 'negocio_id': negocio_actual} )

@login_required(login_url="/")
def agregar_proveedor(request, pk):
    usu = Usuario.objects.get(id=request.user.id)
    negocioo = Negocio.objects.get(id=pk)
    print(negocioo)
    print('-----------------')
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
    negocio_producto = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)

    return render(request, 'app/producto/view_producto.html', {'negocio_producto':negocio_producto, 'negocio_id': negocio} )

@login_required(login_url="/")
def agregar_producto(request, pk):

    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
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
    return render(request, 'app/compra/view_compra.html',{'negocio_id': negocio})

@login_required(login_url="/")
def view_de_reportes_compra(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    return render(request, 'app/compra/view_reportes_compra.html',{'negocio_id': negocio})

@login_required(login_url="/")
def list_compras(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
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

@login_required(login_url="/")
def list_compras_reportes(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
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
    return render(request, 'app/venta/view_venta.html',{'negocio_id': negocio})

@login_required(login_url="/")
def view_de_reportes_venta(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
    return render(request, 'app/venta/view_reportes_venta.html',{'negocio_id': negocio})

@login_required(login_url="/")
def list_ventas(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
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

@login_required(login_url="/")
def list_ventas_reportes(request, pk):
    usuario = Usuario.objects.get(id=request.user.id)
    negocio = Negocio.objects.get(id=pk)
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
    except:
        return render(request, 'app/error.html', {'negocio_id': negocio} )

@login_required(login_url="/")
def datos_agregar_venta(request, pk):
    negocio = Negocio.objects.get(id=pk)
    detalle_producto_negocio = detalle_negocio_producto.objects.filter(negocio_id=negocio.id, producto_id__isnull=False)
    dic = {}
    for x in detalle_producto_negocio:
        dic[x.producto_id.id]=[x.producto_id.id,x.producto_id.nombre,x.producto_id.stock]

    print(dic)
    return HttpResponse(toJSON(dic), content_type='application/json')

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
