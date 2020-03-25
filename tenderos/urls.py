from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from main.views import *

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', login , name='login' ),
    path('principal', principal_app, name='principal_app' ),

    # path('login', login , name='login' ),
    path('logout', logout, name = 'logout' ),
    re_path('usuario/perfil/(?P<pk>\d+)/', perfil_usuario, name='perfil_usuario'),
    path('corporativo', view_corporativo, name='view_corporativo' ),

    path('pabellones/', view_pabellon, name='view_pabellon'),
    path('pabellones/nuevo/', registrar_pabellon, name='registrar_pabellon'),

    path('comerciantes', view_comerciantes, name='view_comerciantes' ),
    path('comerciantes/nuevo', registrar_comerciante, name='registrar_comerciante' ),

    path('negocios/', view_negocio, name='view_negocio'),
    path('negocios/nuevo/', registrar_negocio, name='registrar_negocio'),

    path('compras/', view_de_compra, name='view_compra'),
    re_path('compras/lista/(?P<pk>\d+)/', list_compras, name='lista_de_compra'),
    re_path('compras/lista/detalle/(?P<pk>\d+)/', detalle_de_compra, name='detalles_compras'),
    re_path('compras/lista/detalle/editar_item/(?P<pk>\d+)/', editar_item_detalle_compra, name='editar_item_detalle_compra'),
    re_path('compras/lista/detalle/eliminar_item/(?P<pk>\d+)/', eliminar_item_detalle_compra, name='eliminar_item_detalle_compra'),
    re_path('compras/nuevo/(?P<pk>\d+)/', agregar_compra, name='agregar_compra'),
    re_path('compras/eliminar/(?P<pk>\d+)/', eliminar_compra, name='eliminar_compra'),

    path('ventas/', view_de_venta, name='view_venta'),
    path('ventas/reportes', view_de_reportes_venta, name='view_de_reportes_venta'),
    re_path('ventas/lista/(?P<pk>\d+)/', list_ventas, name='lista_de_venta'),
    re_path('ventas/lista/detalle/(?P<pk>\d+)/', detalle_de_venta, name='detalles_ventas'),
    re_path('ventas/lista/detalle/editar_item/(?P<pk>\d+)/', editar_item_detalle_venta, name='editar_item_detalle_venta'),
    re_path('ventas/lista/detalle/eliminar_item/(?P<pk>\d+)/', eliminar_item_detalle_venta, name='eliminar_item_detalle_venta'),
    re_path('ventas/nuevo/(?P<pk>\d+)/', agregar_venta, name='agregar_venta'),
    re_path('ventas/eliminar/(?P<pk>\d+)/', eliminar_venta, name='eliminar_venta'),

    re_path('proveedores/(?P<pk>\d+)/', view_proveedor, name='view_proveedor'),
    re_path('proveedores/nuevo/(?P<pk>\d+)/', agregar_proveedor, name='agregar_proveedor'),
    re_path('proveedores/editar/(?P<pk>\d+)/', editar_proveedor, name='editar_proveedor'),
    re_path('proveedores/eliminar/(?P<pk>\d+)/', eliminar_proveedor, name='eliminar_proveedor'),

    re_path('productos/(?P<pk>\d+)/', view_producto, name='view_producto'),
    re_path('productos/nuevo/(?P<pk>\d+)/', agregar_producto, name='agregar_producto'),
    re_path('productos/detalle/producto/(?P<pk>\d+)/', detalle_producto, name='detalle_producto'),
    re_path('productos/eliminar/(?P<pk>\d+)/', eliminar_producto, name='eliminar_producto'),

    re_path('administracion/nuevoempleado/(?P<pk>\d+)/', registrar_empleado, name='registrar_empleado'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
