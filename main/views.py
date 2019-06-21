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
def view_compra(request):
    return render(request, 'app/compra/view_compra.html')

@login_required(login_url="/")
def view_proveedor(request, pk):
    usuario = User.objects.get(id=pk)
    usuario_proveedor = detalle_usuario_producto.objects.filter(usuario_id=usuario.id)
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


# def actualizar_docente(request):
#     controller = Controller_docente()
#     idd = request.POST.get('id')
#     docente = {'id':idd}
#     for key in docente:
#         print key, ":", docente[key]
#     resul = controller.listar_mostrar_docentes(docente)
#     dic = {'resul':resul }

#     return HttpResponse(toJSON(dic), content_type='application/json')

# def actualizar_guardar_docente(request):
#     controller = Controller_docente()
#     idd = request.POST.get('id')
#     docente1 = request.POST.get('nombre')
#     docente2 = request.POST.get('apellido')
#     docente3 = request.POST.get('cedula')
#     docente = {'id':idd, 'nombre':docente1, 'apellido':docente2, 'cedula':docente3}
#     for key in docente:
#         print key, ":", docente[key]
#     resul = controller.actualizar_docentes(docente)
#     dic = {'resul':resul }

#     return HttpResponse(toJSON(dic), content_type='application/json')