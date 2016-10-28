from django.test import TestCase
from ..templatetags.custom_filters import currency, set_user_locale
from django.utils.translation import to_locale, get_language, override
import locale


class TestCurrencyTag(TestCase):
    def setUp(self):
        self.value_empty_str = ''
        self.value_str = 'a'
        self.value_float = 12.5
        self.locale = 'pt-br'

    def test_value_empty_string(self):
        self.assertEqual(currency(self.value_empty_str), '')

    def test_value_not_float_convertible(self):
        self.assertEqual(currency(self.value_str), 'a')

    def test_value_float(self):
        user_locale = to_locale(get_language())
        set_user_locale(user_locale)
        self.assertEqual(currency(self.value_float), locale.currency(self.value_float, grouping=True))

    @override('pt-br')
    def test_overridden_locale_float(self):
        user_locale = to_locale(get_language())
        set_user_locale(user_locale)
        self.assertEqual(currency(self.value_float), locale.currency(self.value_float, grouping=True))


class TestSetUserLocale(TestCase):
    def setUp(self):
        self.locale_c = 'C'
        self.locale_none = None

    def test_locale_is_c(self):
        self.assertEqual(set_user_locale(self.locale_c), 'en_US')

    def test_locale_is_none(self):
        self.assertEqual(set_user_locale(self.locale_none), 'en_US')

    def test_default_client_locale(self):
        user_locale = to_locale(get_language())
        self.assertEqual(set_user_locale(user_locale), user_locale)

    @override('pt-br')
    def test_overridden_client_locale(self):
        user_locale = to_locale(get_language())
        self.assertEqual(set_user_locale(user_locale), user_locale)
