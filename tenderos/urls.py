from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from main.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', index, name='index' ),
    path('principal', principal_app, name='principal_app' ),

    path('login', login , name='login' ),
    path('logout', logout, name = 'logout' ),
    path('registrar', registrar_comerciante, name='registrar_comerciante' ),

    path('compra', view_compra, name='view_compra'),
]
