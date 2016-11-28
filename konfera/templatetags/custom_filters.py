from django import template


from konfera.utils import currency_round_up
from konfera.settings import CURRENCY

register = template.Library()


@register.filter
def currency(value):
    if str(value).replace('.', '').replace('-', '').isdigit():
        return '%s %s' % (currency_round_up(value), CURRENCY[0])
    else:
        return value


@register.filter
def currency_code(value):
    if str(value).replace('.', '').replace('-', '').isdigit():
        return '%s %s' % (currency_round_up(value), CURRENCY[1])
    else:
        return value
