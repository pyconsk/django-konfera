import random
import string
from django.test import override_settings
from functools import wraps
from konfera import settings
try:
    from importlib import reload
except ImportError:
    from imp import reload


def random_string(length=1, unicode=False):
    """
    Returns random ascii or unicode string.
    """
    if unicode:
        def random_fun():
            return chr(random.choice((0x300, 0x2000)) + random.randint(0, 0xff))
    else:
        def random_fun():
            return random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits)

    return ''.join(random_fun() for _ in range(length))


def custom_override_settings(**settings_kwargs):
    """
    Override the settings as override_settings from django.
    This decorator also reloads the settings.py module so the settings are changed as expected.
    """
    def _my_decorator(func):
        @override_settings(**settings_kwargs)
        def _decorator(func2, *args, **kwargs):
            reload(settings)
            return func(func2, *args, **kwargs)
        return wraps(func)(_decorator)
    return _my_decorator

