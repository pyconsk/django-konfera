from django import template
from django.utils.translation import get_language, to_locale
from django.utils.encoding import get_system_encoding
import locale

register = template.Library()


def set_default_locale():
    default_language = get_language()
    default_loc = to_locale(default_language)
    system_enc = get_system_encoding()
    try:
        user_locale = locale.setlocale(locale.LC_ALL, (default_loc, system_enc))
    except locale.Error:
        user_locale = locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
    return user_locale


@register.filter
def currency(value):
    set_default_locale()
    try:
        value = float(value)
    except ValueError:
        return value
    return locale.currency(value, grouping=True)
