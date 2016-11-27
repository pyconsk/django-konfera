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
Specify url, where user will be redirected after registering the ticket.
"""
ORDER_REDIRECT = getattr(settings, 'ORDER_REDIRECT', 'order_details')

"""
Register email notification.
"""
REGISTER_EMAIL_NOTIFY = getattr(settings, 'REGISTER_EMAIL_NOTIFY', False)
REGISTER_EMAIL_BCC = getattr(settings, 'REGISTER_EMAIL_BCC', [])

"""Notify after submitting proposal"""
PROPOSAL_NOTIFY = getattr(settings, 'PROPOSAL_NOTIFY', False)
