from django.test import TestCase
from ..templatetags.custom_filters import currency, set_user_locale
import locale


class TestCurrencyTag(TestCase):
    def setUp(self):
        self.value_str = ''
        self.value_float = 12.5

    def test_value_not_float_convertible(self):
        self.assertEqual(currency(self.value_str), '')

    def test_value_float(self):
        user_locale = locale.setlocale(locale.LC_ALL, '')
        if user_locale in ['C', None]:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        self.assertEqual(currency(self.value_float), locale.currency(self.value_float, grouping=True))


class TestSetUserLocale(TestCase):
    def setUp(self):
        self.locale_c = 'C'
        self.locale_none = None

    def test_locale_is_c(self):
        self.assertEqual(set_user_locale(self.locale_c), 'en_US.UTF-8')

    def test_locale_is_none(self):
        self.assertEqual(set_user_locale(self.locale_none), 'en_US.UTF-8')

    def test_user_locale(self):
        user_locale = locale.setlocale(locale.LC_ALL, '')
        self.assertEqual(set_user_locale(), user_locale)
