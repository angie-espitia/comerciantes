from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime

## subir imagenes por carpeta de usuario
def get_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
	print(instance)
	try:
		detalle_negocio = detalle_negocio_producto.objects.filter(negocio_id=instance.id)

		for row in detalle_negocio:
			negocio = row.negocio_id
		return 'negocio_{0}/{1}'.format(negocio, filename)
	except:
		print('sisirvioxd')
		return 'corporativo/{0}'.format(filename)

# Manejo de usuarios
class Usuario(models.Model):
	id = models.OneToOneField(User, primary_key=True, on_delete=models.DO_NOTHING)
	documento = models.CharField(max_length = 45)
	telefono = models.CharField(max_length = 45, null=True)
	direccion = models.CharField(max_length = 45, null=True)
	foto = models.ImageField( upload_to=get_upload_path, null=True) #default="../static/my/img/img4.jpg"

	# class Meta:
	# 	db_table = 'Usuario'
	# 	managed  = False

	def __str__(self):
		return '{}'.format(self.id)

#Manejo negocio
class Pabellon(models.Model):
	id = models.AutoField( primary_key=True)
	nombre = models.CharField(max_length = 45 )
	descripcion = models.TextField( null=True)

	# class Meta:
	# 	db_table = 'Pabellon'
	# 	managed  = False

	def __str__(self):
		return '{}'.format(self.nombre)

class Negocio(models.Model):
	id = models.AutoField( primary_key=True)
	nombre = models.CharField(max_length = 45)
	nit = models.CharField(max_length = 45, null=True, unique=True)
	telefono = models.CharField(max_length = 45, null=True)
	email = models.CharField(max_length = 45, null=True)
	pabellon_id = models.ForeignKey(Pabellon, on_delete=models.DO_NOTHING)

	# class Meta:
	# 	db_table = 'Negocio'
	# 	managed  = False

	def __str__(self):
		return '{}'.format(self.nombre)

# Manejo de negocio tenderos
class Proveedor(models.Model):
	id = models.AutoField( primary_key=True )
	razon_social = models.CharField(max_length = 45)
	nombre = models.CharField(max_length = 45)
	telefono = models.CharField(max_length = 45, null=True)
	direccion = models.CharField(max_length = 45, null=True)
	celular = models.CharField(max_length = 45, null=True)
	email = models.CharField(max_length = 45, null=True)

	# class Meta:
	# 	db_table = 'Proveedor'
	# 	managed  = False

	def __str__(self):
		return '{}'.format(self.razon_social)

class Compra(models.Model):
	id = models.AutoField( primary_key=True)
	fecha = models.DateField()
	total = models.IntegerField()

	# class Meta:
	# 	db_table = 'Compra'
	# 	managed  = False

	def __str__(self):
		return '{}'.format(self.id)

class Venta(models.Model):
	id = models.AutoField( primary_key=True)
	fecha = models.DateField()
	total = models.IntegerField()
	observacion = models.CharField(max_length = 45, null=True)

	# class Meta:
	# 	db_table = 'Venta'
	# 	managed  = False

	def __str__(self):
		return '{}'.format(self.id)

class unidad_medida(models.Model):
	id = models.AutoField( primary_key=True)
	nombre_unidad = models.CharField(max_length = 45)
	abreviatura_unidad = models.CharField(max_length = 45)

	# class Meta:
	# 	db_table = 'unidad_medida'
	# 	managed  = False

	def __str__(self):
		return '{}'.format(self.nombre_unidad)

list_estado = ( ('1', 'Activo') , ('2', 'Finalizado'))
class Producto(models.Model):
	id = models.AutoField( primary_key=True)
	nombre = models.CharField(max_length = 45)
	stock = models.IntegerField()
	valor_costo = models.IntegerField()
	valor_venta = models.IntegerField()
	imagen = models.ImageField( upload_to=get_upload_path , null=True) #default="../static/my/img/img4.jpg"
	descripcion = models.TextField( null=True)
	estado = models.CharField(max_length=1 , choices = list_estado)
	unidad_medida_id = models.ForeignKey(unidad_medida , on_delete=models.DO_NOTHING)

	# class Meta:
	# 	db_table = 'Producto'
	# 	managed  = False

	def __str__(self):
		return '{}'.format(self.nombre)

class detalle_compra(models.Model):
	id = models.AutoField( primary_key=True)
	compra_id = models.ForeignKey(Compra, on_delete=models.DO_NOTHING)
	producto_id = models.ForeignKey(Producto , on_delete=models.DO_NOTHING)
	proveedor_id = models.ForeignKey(Proveedor , on_delete=models.DO_NOTHING)
	cantidad = models.IntegerField()
	cantidad_stock_momento = models.IntegerField()
	cantidad_stock_anterior = models.IntegerField()
	valor_unitario = models.IntegerField()
	total_producto = models.IntegerField()

	# class Meta:
	# 	db_table = 'detalle_compra'
	# 	managed  = False

class detalle_venta(models.Model):
	id = models.AutoField( primary_key=True)
	venta_id = models.ForeignKey(Venta, on_delete=models.DO_NOTHING)
	producto_id = models.ForeignKey(Producto , on_delete=models.DO_NOTHING)
	cantidad = models.IntegerField()
	cantidad_stock_momento = models.IntegerField()
	cantidad_stock_anterior = models.IntegerField()
	total_producto = models.IntegerField()

	# class Meta:
	# 	db_table = 'detalle_venta'
	# 	managed  = False

class detalle_negocio_producto(models.Model):
	id = models.AutoField( primary_key=True)
	negocio_id = models.ForeignKey(Negocio, on_delete=models.DO_NOTHING)
	producto_id = models.ForeignKey(Producto , on_delete=models.DO_NOTHING, null=True)
	proveedor_id = models.ForeignKey(Proveedor , on_delete=models.DO_NOTHING)

	# class Meta:
	# 	db_table = 'detalle_negocio_producto'
	# 	managed  = False

class detalle_usuario_negocio(models.Model):
	id = models.AutoField( primary_key=True)
	negocio_id = models.ForeignKey(Negocio, on_delete=models.DO_NOTHING)
	usuario_id = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING)

	# class Meta:
	# 	db_table = 'detalle_usuario_negocio'
	# 	managed  = False

class Log(models.Model):
	id = models.AutoField( primary_key=True)
	usuario = models.IntegerField()
	negocio = models.IntegerField()
	tiempo= models.DateField( default=datetime.datetime.now)
	accion= models.TextField()

	# class Meta:
	# 	db_table = 'Log'
	# 	managed  = False
