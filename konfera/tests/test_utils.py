from django.test import TestCase

from konfera.models.email_template import EmailTemplate
from konfera.utils import validate_email_template, get_email_template, EmailTemplateError


class EmailUtilTest(TestCase):

    def test_validate_email_template(self):
        template = 'Hello {name}'
        valid_input = {'name': 'Joe'}
        invalid_input = {'Joe': 'name'}
        self.assertEqual(validate_email_template(template, valid_input), 'Hello Joe')
        self.assertRaises(EmailTemplateError, validate_email_template, *(template, invalid_input))
        self.assertEqual(validate_email_template(template, {}, False), 'Hello {name}')

    def test_get_email_template(self):
        template = 'Non existing test template'
        self.assertRaises(EmailTemplateError, get_email_template, template)
        et = EmailTemplate.objects.create(name=template)
        self.assertEqual(get_email_template(template), et)
