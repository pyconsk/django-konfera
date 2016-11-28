from django.test import TestCase

from konfera.templatetags.custom_filters import currency, currency_code
from konfera.settings import CURRENCY


class TestCurrencyTag(TestCase):
    def setUp(self):
        self.value_empty_str = ''
        self.value_str = 'a'
        self.value_float = 12.5
        self.value_negative_int = -12582
        self.value_int = 2
        self.value_str_int = '-5'

    def test_value_empty_string(self):
        self.assertEqual(currency(self.value_empty_str), self.value_empty_str)
        self.assertEqual(currency_code(self.value_empty_str), self.value_empty_str)

    def test_value_not_float_convertible(self):
        self.assertEqual(currency(self.value_str), self.value_str)
        self.assertEqual(currency_code(self.value_str), self.value_str)

    def test_value_float(self):
        self.assertEqual(currency(self.value_float), '%s %s' % (self.value_float, CURRENCY[0]))
        self.assertEqual(currency_code(self.value_float), '%s %s' % (self.value_float, CURRENCY[1]))

    def test_value_negative_int(self):
        self.assertEqual(currency(self.value_negative_int), '%s %s' % (self.value_negative_int, CURRENCY[0]))
        self.assertEqual(currency_code(self.value_negative_int), '%s %s' % (self.value_negative_int, CURRENCY[1]))

    def test_value_int(self):
        self.assertEqual(currency(self.value_int), '%s %s' % (self.value_int, CURRENCY[0]))
        self.assertEqual(currency_code(self.value_int), '%s %s' % (self.value_int, CURRENCY[1]))

    def test_value_str_int(self):
        self.assertEqual(currency(self.value_str_int), '%s %s' % (self.value_str_int, CURRENCY[0]))
        self.assertEqual(currency_code(self.value_str_int), '%s %s' % (self.value_str_int, CURRENCY[1]))

