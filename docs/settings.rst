List of settings
================

Configuration options available for django-konfera, to modify application according your needs. Knowing this list of settings can save you a lot of time. You can define any of this settings in you project's local settings file. 

Here’s a full list of all available settings, and their default values.

All settings described here can be found in ``konfera/settings.py``.


GOOGLE_ANALYTICS
----------------

**Default value:** ``None`` 

Analytics code format: 'UA-XXXXXXXX-X'. If defined, Google analytics code is generated on all pages. This one can be overwritten per event, in event details. 



NAVIGATION_ENABLED
------------------

**Default value:** ``False`` 



NAVIGATION_BRAND
----------------

**Default value:** ``'Konfera'`` 



NAVIGATION_URL
--------------

**Default value:** ``'/'`` 



NAVIGATION_LOGO
---------------

**Default value:** ``None`` 

Application supports django-sitetree navigation support, weather it should be passed to template.



CURRENCY
--------

**Default value:** ``('€', 'EUR')``

Currency used in the application. (Currently support just one currency). Defined as tuple of Currency Symbol (Unicode block) and  Currency code (ISO 4217)



TALK_LANGUAGE
-------------

**Default value:** ``(('SK', _('Slovak')), ('CZ', _('Czech')), ('EN', _('English')),)``



TALK_LANGUAGE_DEFAULT
---------------------

**Default value:** ``EN`` 



TALK_DURATION
-------------

**Default value:** ``((5, _('5 min')), (30, _('30 min')), (45, _('45 min')),)``



LANDING_PAGE
------------

**Default value:** ``latest_conference`` 

Setting is a composite of two keywords: *<timewise>_<event>*
 * *<timewise>* can be: latest or earliest
 * *<event>* can be: conference or meetup

possible combinations: 
 * latest_conference (DEFAULT)
 * latest_meetup 
 * earliest_conference
 * earliest_meetup



ORDER_REDIRECT
--------------

**Default value:** ``order_detail`` 

Specify url, where user will be redirected after registering the ticket.



REGISTER_EMAIL_NOTIFY
---------------------

**Default value:** ``False`` 

Register email notification.



PROPOSAL_EMAIL_NOTIFY
---------------------

**Default value:** ``False`` 

Notify after submitting proposal



EMAIL_NOTIFY_BCC
----------------

**Default value:** ``[]`` 

Universal BCC for all notifications, MUST be empty list OR list of valid email adresses



UNPAID_ORDER_NOTIFICATION_REPEAT
--------------------------------

**Default value:** ``3`` 

How many times we should repeat the email notification



UNPAID_ORDER_NOTIFICATION_REPEAT_DELAY
--------------------------------------

**Default value:** ``5`` 

How long should we wait to notify about missing payment



SITE_URL
--------

**Default value:** ``'https://www.pycon.sk'`` 

Absolute url base with protocol, should not contain trailing slash (/) at the end



ENABLE_ORDER_PDF_GENERATION
---------------------------

**Default value:** ``False`` 

Enable ability to store order as PDF. In order to make this functionality work, make sure django-wkhtmltopdf, with wkhtmltopdf binary.
