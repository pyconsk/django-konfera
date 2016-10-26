from django import template
import locale

register = template.Library()

user_locale = locale.setlocale(locale.LC_ALL, '')
if user_locale == 'C' or user_locale is None:
    locale.setlocale(locale.LC_ALL, 'en_US')


@register.filter
def currency(value):
    try:
        value = float(value)
    except ValueError:
        return value
    return locale.currency(value, grouping=True)
