from django.test import TestCase

from konfera.utils import EmailTemplateError, validate_email_template


class EmailUtilTest(TestCase):
    def setUp(self):
        self.addresses = {'to': ['noone@example.com']}
        self.subject = 'Subject'
        self.valid_input = {'name': 'Joe'}
        self.text_template = 'Hello {name}'
        self.empty = 'empty_template'

    def test_validate_email_template(self):
        invalid_input = {'Joe': 'name'}
        self.assertEqual(validate_email_template(self.text_template, self.valid_input), 'Hello Joe')
        self.assertRaises(EmailTemplateError, validate_email_template, *(self.text_template, invalid_input))
        self.assertEqual(validate_email_template(self.text_template, {}, False), 'Hello {name}')
