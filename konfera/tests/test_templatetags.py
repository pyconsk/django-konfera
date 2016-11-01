from django.test import TestCase
from ..templatetags.custom_filters import currency, set_default_locale
from django.utils.translation import override
import locale


class TestCurrencyTag(TestCase):
    def setUp(self):
        self.value_empty_str = ''
        self.value_str = 'a'
        self.value_float = 12.5

    def test_value_empty_string(self):
        self.assertEqual(currency(self.value_empty_str), self.value_empty_str)

    def test_value_not_float_convertible(self):
        self.assertEqual(currency(self.value_str), self.value_str)

    def test_value_float(self):
        set_default_locale()
        self.assertEqual(currency(self.value_float), locale.currency(self.value_float, grouping=True))

    @override('en-gb')
    def test_overridden_locale_float(self):
        set_default_locale()
        self.assertEqual(currency(self.value_float), locale.currency(self.value_float, grouping=True))


class TestSetUserLocale(TestCase):
    def test_locale_is_en_US(self):
        self.assertEqual(set_default_locale(), 'en_US.UTF-8')
