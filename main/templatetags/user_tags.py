# -*- coding:utf-8 -*-
from __future__ import unicode_literals

# Core Django imports
from django import template
from django.contrib.auth.models import User, Group
from main.models import Usuario, Negocio

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.filter(name='get_name_negocio')
def get_name_negocio(negocio):
    # print(user.id)
    # usuario = Usuario.objects.get(id=user.id)
    negocio = Negocio.objects.get(id=negocio)
    print(negocio)
    return negocio.nombre
