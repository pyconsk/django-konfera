from django import template
import locale

register = template.Library()


def set_default_locale():
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
