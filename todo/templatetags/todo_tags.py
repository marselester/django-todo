# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter
def mul(value, argument):
    """Multiplies the argument to the value."""
    return int(value) * int(argument)
