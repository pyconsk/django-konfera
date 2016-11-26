from functools import wraps

try:
    from importlib import reload
except ImportError:
    from imp import reload

from django.test import override_settings

from payments import settings


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
