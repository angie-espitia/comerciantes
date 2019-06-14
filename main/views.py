from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.template import RequestContext
from main.validator import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from main.models import *

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