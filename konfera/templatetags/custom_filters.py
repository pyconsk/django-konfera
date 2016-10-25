from django import template
import locale

locale.setlocale(locale.LC_ALL, '')
register = template.Library()


@register.filter
def currency(value):
    try:
        value = float(value)
    except ValueError:
        return value
    return locale.currency(value, grouping=True)
