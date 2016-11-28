from decimal import Decimal

from django.test import TestCase

from konfera.templatetags.custom_filters import currency, currency_code
from konfera.settings import CURRENCY


class TestCurrencyTag(TestCase):
    def setUp(self):
        self.value_empty_str = ''
        self.value_str = 'some string'
        self.value_float = 12.5
        self.value_negative_int = -12582
        self.value_int = 2
        self.value_str_int = '7'

    def test_value_decimal(self):
        test_subjects = (
            (Decimal('1.54'), '1.54'),
            (Decimal('43.331'), '43.34'),
            (Decimal('12345.67894'), '12345.68'),
            (Decimal('0.9999999'), '1.00'),
            (Decimal('-2.31'), '-2.31'),
            (Decimal('-71.455'), '-71.46'),
        )
        for subj in test_subjects:
            self.assertEqual(currency(subj[0]), '%s %s' % (subj[1], CURRENCY[0]))
            self.assertEqual(currency_code(subj[0]), '%s %s' % (subj[1], CURRENCY[1]))

    def test_value_empty_string(self):
        self.assertRaises(AttributeError, currency, self.value_empty_str)
        self.assertRaises(AttributeError, currency_code, self.value_empty_str)

    def test_value_string(self):
        self.assertRaises(AttributeError, currency, self.value_str)
        self.assertRaises(AttributeError, currency_code, self.value_str)

    def test_value_float(self):
        self.assertRaises(AttributeError, currency, self.value_float)
        self.assertRaises(AttributeError, currency_code, self.value_float)

    def test_value_negative_int(self):
        self.assertRaises(AttributeError, currency, self.value_negative_int)
        self.assertRaises(AttributeError, currency_code, self.value_negative_int)

    def test_value_int(self):
        self.assertRaises(AttributeError, currency, self.value_int)
        self.assertRaises(AttributeError, currency_code, self.value_int)

    def test_value_str_int(self):
        self.assertRaises(AttributeError, currency, self.value_str_int)
        self.assertRaises(AttributeError, currency_code, self.value_str_int)
