from django.contrib import admin
from django.urls import path, re_path
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
    re_path('proveedores/(?P<pk>\d+)/', view_proveedor, name='view_proveedor'),
    re_path('proveedores/nuevo/(?P<pk>\d+)/', agregar_proveedor, name='agregar_proveedor'),
    re_path('proveedores/editar/(?P<pk>\d+)/', editar_proveedor, name='editar_proveedor'),
    re_path('proveedores/eliminar/(?P<pk>\d+)/', eliminar_proveedor, name='eliminar_proveedor'),

    re_path('productos/(?P<pk>\d+)/', view_producto, name='view_producto'),
    re_path('productos/nuevo/(?P<pk>\d+)/', agregar_producto, name='agregar_producto'),
    re_path('productos/editar/(?P<pk>\d+)/', editar_producto, name='editar_producto'),
    re_path('productos/eliminar/(?P<pk>\d+)/', eliminar_producto, name='eliminar_producto'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
