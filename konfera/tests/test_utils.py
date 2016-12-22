from django.test import TestCase

from konfera.utils import validate_email_template


class EmailUtilTest(TestCase):

    def test_validate_email_template(self):
        template = 'Hello {name}'
        valid_input = {'name': 'Joe'}
        invalid_input = {'Joe': 'name'}
        self.assertEqual(validate_email_template(template, valid_input), 'Hello Joe')
        self.assertEqual(validate_email_template(template, invalid_input), None)
