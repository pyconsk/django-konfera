from django.utils.translation import ugettext_lazy as _
from django.conf import settings


GOOGLE_ANALYTICS = getattr(settings, 'GOOGLE_ANALYTICS', None)  # just define analytics code: 'UA-XXXXXXXX-X'

"""
Currency used in the application. (Currently support just one currency).
Defined as tuple of Currency Symbol (Unicode block) and  Currency code (ISO 4217)
"""
CURRENCY = getattr(settings, 'CURRENCY', ('€', 'EUR'))

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

"""
Notify after submitting proposal
"""
PROPOSAL_EMAIL_NOTIFY = getattr(settings, 'PROPOSAL_EMAIL_NOTIFY', False)

"""
Universal BCC for all notifications
"""
EMAIL_NOTIFY_BCC = getattr(settings, 'EMAIL_NOTIFY_BCC', [])


"""
Number of days after the user is notified about unpaid order
"""
UNPAID_ORDER_NOTIFICATION_DAYS = getattr(settings, 'UNPAID_ORDER_NOTIFICATION_DAYS', 3)
