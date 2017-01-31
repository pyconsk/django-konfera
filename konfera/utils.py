import re
import logging
from decimal import Decimal, ROUND_UP
from smtplib import SMTPException

from django.core.mail import EmailMultiAlternatives

from konfera.models.email_template import EmailTemplate
from konfera.models.sponsor import Sponsor
from konfera.models.order import Order
from konfera.settings import (GOOGLE_ANALYTICS, GOOGLE_ANALYTICS_ECOMMERCE, NAVIGATION_ENABLED, NAVIGATION_URL,
                              NAVIGATION_LOGO, NAVIGATION_BRAND, EMAIL_NOTIFY_BCC, CURRENCY)


logger = logging.getLogger(__name__)


def collect_view_data(request):
    """
    Function collects view_data generated by other functions
    """
    view_data = dict()
    view_data['navigation_enabled'] = NAVIGATION_ENABLED
    view_data['navigation_url'] = NAVIGATION_URL
    view_data['navigation_brand'] = NAVIGATION_BRAND
    view_data['navigation_logo'] = NAVIGATION_LOGO
    view_data['footer_enabled'] = True

    if GOOGLE_ANALYTICS:
        view_data['ga'] = GOOGLE_ANALYTICS

    return view_data


def update_order_status_context(status, context):
    if status == Order.PAID:
        context['status_label'] = 'label-success'
    elif status in [Order.CANCELLED, Order.EXPIRED]:
        context['status_label'] = 'label-danger'
    else:
        context['status_label'] = 'label-warning'


def update_event_context(event, context, show_sponsors=True):
    context['event'] = event

    if show_sponsors:
        frontend_sponsors = (Sponsor.PLATINUM, Sponsor.GOLD, Sponsor.SILVER, Sponsor.MEDIA)
        context['sponsors'] = event.sponsors.filter(type__in=frontend_sponsors).order_by('type', 'title')

    if event.analytics:
        context['ga'] = event.analytics


def generate_ga_ecommerce_context(order, context):

    if GOOGLE_ANALYTICS and GOOGLE_ANALYTICS_ECOMMERCE:
        ga_transaction = {
            'id': order.variable_symbol,
            'affiliation': order.event,
            'revenue': order.price,
            'shipping': '0',
            'tax': '0',
            'currency': CURRENCY[1],
        }
        ga_items = []

        for ticket in order.ticket_set.all():
            ga_items.append({
                'id': order.variable_symbol,
                'name': ticket.type.title,
                'category': ticket.type.attendee_type,
                'price': ticket.type.price,
                'quantity': '1',
                'currency': CURRENCY[1],
            })

        context['ga_ecommerce'] = {
            'ga_transaction': ga_transaction,
            'ga_items': ga_items
        }


def currency_round_up(money):
    return money.quantize(Decimal('1.00'), rounding=ROUND_UP)


class EmailTemplateError(Exception):
    pass


def validate_email_template(raw_template, formatting_dict, required=True):
    required_keys = set(re.findall('{(.+?)}', raw_template))
    if not required_keys.issubset(set(formatting_dict.keys())):
        if required:
            logger.critical('Not all required fields of the template were found in formatting dictionary.\n'
                            'required:{} !~ formatting:{}'.format(required_keys, set(formatting_dict)))
            raise EmailTemplateError('Not all required fields of the template were found in formatting dictionary.\n'
                                     'required:{} !~ formatting:{}'.format(required_keys, set(formatting_dict)))
        else:
            logger.warning('Not all required fields of the template were found in formatting dictionary.')
            return raw_template

    return raw_template.format(**formatting_dict)


def get_email_template(template_name):
    try:
        template = EmailTemplate.objects.get(name=template_name)
        return template
    except EmailTemplate.DoesNotExist:
        raise EmailTemplateError('No such template: {}'.format(template_name))


def send_email(addresses, subject, template_name, formatting_dict=None, **kwargs):
    formatting_dict = formatting_dict or {}
    template = get_email_template(template_name)
    text_template = getattr(template, 'text_template', '')
    html_template = getattr(template, 'html_template', '')

    if not text_template:
        logger.critical('Missing text template (required) for the input {}.'.format(text_template))
        raise EmailTemplateError("Email template is not valid for the input.")
    if not html_template:
        logger.warning('Invalid html template (not required) for the input {}.'.format(html_template))

    text_content = validate_email_template(text_template, formatting_dict)
    html_content = validate_email_template(html_template, formatting_dict, False)

    to = addresses.get('to', [])
    cc = addresses.get('cc', [])
    bcc = addresses.get('bcc', EMAIL_NOTIFY_BCC)

    msg = EmailMultiAlternatives(subject, text_content, to=to, cc=cc, bcc=bcc)
    if html_content:
        msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except (SMTPException, ConnectionRefusedError) as e:
        logger.critical('Sending email raised an exception: %s', e)
    else:
        # increase count on email_template
        template.add_count()
        if kwargs.get('verbose', 0) > 1:
            print(msg)
        return True
