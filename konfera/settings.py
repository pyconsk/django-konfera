from django.utils.translation import ugettext_lazy as _
from django.conf import settings


GOOGLE_ANALYTICS = getattr(settings, 'GOOGLE_ANALYTICS', None)  # just define analytics code: 'UA-XXXXXXXX-X'

TALK_DURATION = getattr(settings, 'TALK_DURATION',
                        (
                            (5, _('5 min')),
                            (30, _('30 min')),
                            (45, _('45 min')),
                        ))

"""
LANDING PAGE is a composite of two keywords: <timewise>_<event>
<timewise> can be: latest or earliest
<event> can be (at the moment): conference or meetup
possible combinations: latest_conference (DEFAULT), latest_meetup, earliest_conference, earliest_meetup
"""
LANDING_PAGE = getattr(settings, 'LANDING_PAGE', 'latest_conference')

"""
Register email notification.
"""
REGISTER_EMAIL_NOTIFY = getattr(settings, 'REGISTER_EMAIL_NOTIFY', False)
REGISTER_EMAIL_BCC = getattr(settings, 'REGISTER_EMAIL_BCC', [])
REGISTER_EMAIL = getattr(settings, 'REGISTER_EMAIL',
                         'Dear {first_name} {last_name},\n\n'
                         'thank you for purchasing ticket for {event}. Your order details are available at url: '
                         '{order_url}\n\n\n'
                         'Looking forward to see you.\n\n'
                         'PyCon SK team.\n\n'
                         '{event_url}')

REGISTER_EMAIL_HTML = getattr(settings, 'REGISTER_EMAIL_HTML',
                              'Dear {first_name} {last_name},<br /><br />'
                              'thank you for purchasing ticket for <strong><a href="{event_url}">{event}</a>'
                              '</strong>.vYour order details are available at url: <a href="{order_url}">{order_url}'
                              '</a><br /><br /><br />'
                              'Looking forward to see you.<br /><br />'
                              'PyCon SK team.')
