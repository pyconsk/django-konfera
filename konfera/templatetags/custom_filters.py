from django.utils.translation import to_locale, get_language
from django import template
import locale

register = template.Library()


def set_user_locale(loc=''):
    user_locale = locale.setlocale(locale.LC_ALL, loc)
    if user_locale in ['C', None]:
        user_locale = locale.setlocale(locale.LC_ALL, 'en_US')
    return user_locale


@register.filter
def currency(value):
    user_locale = to_locale(get_language())
    set_user_locale(user_locale)
    try:
        value = float(value)
    except ValueError:
        return value
    return locale.currency(value, grouping=True)
