import re
import logging
from decimal import Decimal, ROUND_UP
from smtplib import SMTPException

from django.core.mail import EmailMultiAlternatives
from konfera.models.order import Order
from konfera.settings import GOOGLE_ANALYTICS, NAVIGATION_ENABLED, NAVIGATION_URL, NAVIGATION_LOGO, NAVIGATION_BRAND
from konfera.settings import EMAIL_NOTIFY_BCC


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
        context['sponsors'] = event.sponsors.all().order_by('type', 'title')

    if event.analytics:
        context['ga'] = event.analytics


def currency_round_up(money):
    return money.quantize(Decimal('1.00'), rounding=ROUND_UP)


def validate_email_template(raw_template, formatting_dict):
    required_keys = set(re.findall('{(.+?)}', raw_template))
    if required_keys.issubset(set(formatting_dict.keys())):
        return raw_template.format(**formatting_dict)
    return


class EmailTemplateError(Exception):
    pass


def send_email(addresses, subject, template, formatting_dict=None, verbose=0):
    formatting_dict = formatting_dict or {}
    text_template = getattr(template, 'text_template', '')
    html_template = getattr(template, 'html_template', '')
    text_content = validate_email_template(text_template, formatting_dict)
    html_content = validate_email_template(html_template, formatting_dict)

    if not text_content:
        logger.critical('Invalid text template (required) for the input {}.'.format(text_content))
        # raise EmailTemplateError("Email template is not valid for the input.")
    if not html_content:
        logger.warning('Invalid html template (not required) for the input {}.'.format(html_content))

    to = addresses.get('to', [])
    cc = addresses.get('cc', [])
    bcc = addresses.get('bcc', EMAIL_NOTIFY_BCC)

    # if text template does not match - do we want to raid the exception or to send unformatted template?
    msg = EmailMultiAlternatives(subject, text_content or text_template, to=to, cc=cc, bcc=bcc)
    if html_content:
        msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
    except (SMTPException, ConnectionRefusedError) as e:
        logger.critical('Sending email raised an exception: %s', e)
    else:
        # increase count on email_template
        template.add_count()
        if verbose > 1:
            print(msg)
        return True
