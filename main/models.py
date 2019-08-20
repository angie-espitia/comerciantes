from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Manejo de usuarios

class Usuario(models.Model):
	id = models.OneToOneField(User, primary_key=True, on_delete=models.DO_NOTHING, db_column='id')
	telefono = models.IntegerField( db_column='telefono')
	direccion = models.CharField(max_length = 45, db_column='direccion', null=True)

	class Meta:
		db_table = 'Usuario'
		managed  = False

	def __str__(self):
		return '{}'.format(self.id)

# Manejo de negocio tenderos
class Proveedor(models.Model):
	# id = models.AutoField( primary_key=True, db_column='id')
	nombre = models.CharField(max_length = 45, db_column='nombre')
	razon_social = models.CharField(max_length = 45, db_column='razon_social')
	telefono = models.CharField(max_length = 45, db_column='telefono', null=True)
	direccion = models.CharField(max_length = 45, db_column='direccion', null=True)
	celular = models.CharField(max_length = 45, db_column='celular', null=True)
	email = models.CharField(max_length = 45, db_column='email', null=True)

	class Meta:
		db_table = 'Proveedor'
		managed  = False

	def __str__(self):
		return '{}'.format(self.nombre)

class Compra(models.Model):
	id = models.AutoField( primary_key=True, db_column='id')
	fecha = models.DateField(db_column='fecha')
	total = models.IntegerField( db_column='total')

	class Meta:
		db_table = 'Compra'
		managed  = False

	def __str__(self):
		return '{}'.format(self.id)

class Venta(models.Model):
	id = models.AutoField( primary_key=True, db_column='id')
	fecha = models.DateField(db_column='fecha')
	total = models.IntegerField( db_column='total')
	observacion = models.CharField(max_length = 45, db_column='observacion', null=True)

	class Meta:
		db_table = 'Venta'
		managed  = False

	def __str__(self):
		return '{}'.format(self.id)

## subir imagenes por carpeta de usuario
def get_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    detalle_usuario = detalle_usuario_producto.objects.get(producto_id=instance.id)
    return 'user_{0}/{1}'.format(detalle_usuario.usuario_id.id, filename)

class Producto(models.Model):
	id = models.AutoField( primary_key=True, db_column='id')
	codigo = models.CharField(max_length = 45, db_column='codigo', null=True)
	nombre = models.CharField(max_length = 45, db_column='nombre')
	stock = models.CharField(max_length = 45, db_column='stock')
	valor_costo = models.IntegerField( db_column='valor_costo')
	valor_venta = models.IntegerField( db_column='valor_venta')
	imagen = models.ImageField( upload_to=get_upload_path , db_column='imagen', null=True) #default="../static/my/img/img4.jpg"
	descripcion = models.TextField( db_column='descripcion', null=True)
	
	class Meta:
		db_table = 'Producto'
		managed  = False

	def __str__(self):
		return '{}'.format(self.nombre)

class detalle_compra(models.Model):
	id = models.AutoField( primary_key=True, db_column='id')
	compra_id = models.ForeignKey(Compra, on_delete=models.DO_NOTHING, db_column='compra_id')
	producto_id = models.ForeignKey(Producto , on_delete=models.DO_NOTHING, db_column='producto_id')
	proveedor_id = models.ForeignKey(Proveedor , on_delete=models.DO_NOTHING, db_column='proveedor_id')
	cantidad = models.IntegerField( db_column='cantidad')
	valor_unitario = models.IntegerField( db_column='valor_unitario')
	total_producto = models.IntegerField( db_column='total_producto')

	class Meta:
		db_table = 'detalle_compra'
		managed  = False

class detalle_venta(models.Model):
	id = models.AutoField( primary_key=True, db_column='id')
	venta_id = models.ForeignKey(Venta, on_delete=models.DO_NOTHING, db_column='venta_id')
	producto_id = models.ForeignKey(Producto , on_delete=models.DO_NOTHING, db_column='producto_id')
	cantidad = models.IntegerField( db_column='cantidad')
	total_producto = models.IntegerField( db_column='total_producto')

	class Meta:
		db_table = 'detalle_venta'
		managed  = False

class detalle_usuario_producto(models.Model):
	id = models.AutoField( primary_key=True, db_column='id')
	usuario_id = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING, db_column='usuario_id')
	producto_id = models.ForeignKey(Producto , on_delete=models.DO_NOTHING, db_column='producto_id', null=True)
	proveedor_id = models.ForeignKey(Proveedor , on_delete=models.DO_NOTHING, db_column='proveedor_id')

	class Meta:
		db_table = 'detalle_usuario_producto'
		managed  = False