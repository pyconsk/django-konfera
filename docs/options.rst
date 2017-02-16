Options
=======

How to setup Google Analytics?
------------------------------

Django-konfera has an option to add tracking code for your application just simply use option:

GOOGLE_ANALYTICS = 'UA-XXXXXXXX-X'

Enabling Google Analytics will autoamtically track certain events. The Projct manager can click on sponsors banner or clicking on outbound links. If you add outbound links tracking make sure you have `onclick="ga('send', 'event', 'sponsor', 'click', 'sponsors-panel-{{ sponsor|slugify }}'); trackOutboundLink('{{ sponsor.url }}');` 

For implementing ecommerce tracking with django-konfera, first you need to enable it in your Google Analitcs settings for your account and afterwards just enable option:

GOOGLE_ANALYTICS_ECOMMERCE = True

