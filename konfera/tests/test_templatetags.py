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
    @override('en-us')
    def test_locale_is_en_US(self):
        self.assertEqual(set_default_locale(), 'en_US.UTF-8')

    @override('pt-br')
    def test_unsupported_locale1(self):
        self.assertIn(set_default_locale(), ['pt_BR.UTF-8', 'en_US.UTF-8'])

    @override('zh-cn')
    def test_unsupported_locale2(self):
        self.assertIn(set_default_locale(), ['zh_CN.UTF-8', 'en_US.UTF-8'])

    @override('ro-mo')
    def test_unsupported_locale3(self):
        self.assertIn(set_default_locale(), ['ro_MO.UTF-8', 'en_US.UTF-8'])
