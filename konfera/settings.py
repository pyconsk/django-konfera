from django.utils.translation import ugettext_lazy as _
from django.conf import settings


GOOGLE_ANALYTICS = getattr(settings, 'GOOGLE_ANALYTICS', None)  # just define analytics code: 'UA-XXXXXXXX-X'
GOOGLE_ANALYTICS_ECOMMERCE = getattr(settings, 'GOOGLE_ANALYTICS_ECOMMERCE', False)

"""
Application supports django-sitetree navigation support, weather it shouold be passed to template
"""
NAVIGATION_ENABLED = getattr(settings, 'NAVIGATION_ENABLED', False)
NAVIGATION_BRAND = getattr(settings, 'NAVIGATION_BRAND', 'Konfera')
NAVIGATION_URL = getattr(settings, 'NAVIGATION_URL', '/')
NAVIGATION_LOGO = getattr(settings, 'NAVIGATION_LOGO', None)

"""
Currency used in the application. (Currently support just one currency).
Defined as tuple of Currency Symbol (Unicode block) and  Currency code (ISO 4217)
"""
CURRENCY = getattr(settings, 'CURRENCY', ('€', 'EUR'))

TALK_LANGUAGE = getattr(settings, 'TALK_LANGUAGE',
                        (
                            ('SK', _('Slovak')),
                            ('CZ', _('Czech')),
                            ('EN', _('English')),
                        ))
TALK_LANGUAGE_DEFAULT = 'EN'

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
ORDER_REDIRECT = getattr(settings, 'ORDER_REDIRECT', 'order_detail_thanks')

"""
Register email notification.
"""
REGISTER_EMAIL_NOTIFY = getattr(settings, 'REGISTER_EMAIL_NOTIFY', False)

"""
Notify after submitting proposal
"""
PROPOSAL_EMAIL_NOTIFY = getattr(settings, 'PROPOSAL_EMAIL_NOTIFY', False)

"""
Universal BCC for all notifications, MUST be empty list OR list of valid email adresses
"""
EMAIL_NOTIFY_BCC = getattr(settings, 'EMAIL_NOTIFY_BCC', [])

"""
How many times we should repeat the email notification
"""
UNPAID_ORDER_NOTIFICATION_REPEAT = getattr(settings, 'UNPAID_ORDER_NOTIFICATION_REPEAT', 3)

"""
How long should we wait to notify about missing payment
"""
UNPAID_ORDER_NOTIFICATION_REPEAT_DELAY = getattr(settings, 'UNPAID_ORDER_NOTIFICATION_REPEAT_DELAY', 5)

"""
Absolute url base with protocol, should not contain trailing slash (/) at the end
"""
SITE_URL = getattr(settings, 'ABSOLUTE_URL', 'https://www.pycon.sk').rstrip('/')

"""
Enable ability to store order as PDF.
In order to make this functionality work, make sure django-wkhtmltopdf, with wkhtmltopdf binary.
"""
ENABLE_ORDER_PDF_GENERATION = getattr(settings, 'ENABLE_ORDER_PDF_GENERATION', False)

"""
Show amount of available tickets
"""
DISPLAY_TICKET_AVAILABILITY = getattr(settings, 'DISPLAY_TICKET_AVAILABILITY', True)
