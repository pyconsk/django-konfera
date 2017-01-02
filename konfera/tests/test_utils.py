from django.test import TestCase

from mock import patch

from konfera.models.email_template import EmailTemplate
from konfera.utils import EmailTemplateError, validate_email_template, get_email_template, send_email


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

    def test_get_email_template(self):
        template = 'Non existing test template'
        self.assertRaises(EmailTemplateError, get_email_template, template)
        et = EmailTemplate.objects.create(name=template)
        self.assertEqual(get_email_template(template), et)

    @patch('konfera.utils.logger')
    def test_send_email_missing_template(self, mock_logger):
        et = EmailTemplate.objects.create(name=self.empty)
        send_dict = (self.addresses, self.subject, self.empty, self.valid_input)
        self.assertRaises(EmailTemplateError, send_email, *send_dict)
        self.assertTrue(mock_logger.critical.called)
        et.text_template = self.text_template
        et.save()
        send_email(*send_dict)
        self.assertTrue(mock_logger.warning.called)
