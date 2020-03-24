from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from django.contrib.auth.models import User, Group
from .models import Usuario

# @admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):

    list_display = ('id', 'documento', 'telefono', 'direccion')
    list_display_links = ('id', 'documento', 'telefono', 'direccion')
    # list_editable = ('foto')

class UsuarioInline(admin.StackedInline):

    model = Usuario
    can_delete = False
    verbose_name_plural = 'datos del usuario'
    fk_name = 'id'

class UserAdmin(BaseUserAdmin):
    inlines = [UsuarioInline] # tabla inline
    list_display = ('username', 'first_name', 'last_name', 'email', 'documento', 'telefono', 'direccion', 'foto', 'grupo')
    list_select_related = ('usuario',) #establecer la relacion entre tablas
    list_display_links = ('username',)
    # list_editable = ('first_name', 'last_name', 'email', 'documento', )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name',
    )

    list_filter = (
        'is_active',
        'is_staff',
    )

    def documento(self, instance):
        # definir atributo que esta en otras tablas
        return instance.usuario.documento

    def telefono(self, instance):
        return instance.usuario.telefono

    def direccion(self, instance):
        return instance.usuario.direccion

    def foto(self, instance):
        return instance.usuario.foto

    def grupo(self, instance):
        group =  Group.objects.filter(user = instance)
        for g in group:
            if g.name == 'administrativo':
                return 'Administrativo'
            if g.name == 'propietario_negocio':
                return 'Propietario de Negocio'
            if g.name == 'empleado_negocio':
                return 'Empleado de un Negocio'

    # funcion para quitar los campos de la tabla usuario del formulario
    # def get_inline_instances(self, request, obj=None):
    #     if not obj:
    #         return list()
    #     return super(UserAdmin, self).get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
