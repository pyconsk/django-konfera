from django import template
import locale

register = template.Library()


def set_user_locale(loc=''):
    user_locale = locale.setlocale(locale.LC_ALL, loc)
    if user_locale in ['C', None]:
        user_locale = locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    return user_locale

set_user_locale()


@register.filter
def currency(value):
    try:
        value = float(value)
    except ValueError:
        return value
    return locale.currency(value, grouping=True)
