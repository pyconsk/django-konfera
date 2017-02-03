from django import template

from konfera.utils import currency_round_up
from konfera.settings import CURRENCY

register = template.Library()


@register.filter(name='addcss')
def addcss(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def currency(value):
    return '%s %s' % (currency_round_up(value), CURRENCY[0])


@register.filter
def currency_code(value):
    return '%s %s' % (currency_round_up(value), CURRENCY[1])


@register.filter
def sub(value, arg):
    return value - arg
