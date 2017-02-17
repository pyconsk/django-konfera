.. _installation:

Installation
============

Using Pip
---------

.. code-block:: console

    $ pip install django-konfera



Using the Source
----------------

Get a source tarball from `pypi`_, unpack, then install with:

.. code-block:: console

    $ python setup.py install

.. note:: As an alternative, if you don't want to mess with any packaging tool,
          unpack the tarball and copy/move the modeltranslation directory
          to a path listed in your ``PYTHONPATH`` environment variable.

.. _pypi: http://pypi.python.org/pypi/django-konfera/



Setup
=====

**TODO**



Configuration
=============

Available Settings
------------------

Configuration options available, to modify application according your needs. Knowing this list of settings can save you a lot of time. You can define any of this ``settings.py`` in you project's (local) settings file.

Here’s a full list of all available settings, and their default values. All settings described here can be found in ``konfera/settings.py``.

.. _settings-google_analytics:

``GOOGLE_ANALYTICS``
^^^^^^^^^^^^^^^^^^^^

Default: ``None``

*OPTIONAL* setting. Define your Google analytics code and it will be generated on all pages. 

.. note::
    Google analytics code can be overwritten per event, in event details. 

Example::

    GOOGLE_ANALYTICS = 'UA-XXXXXXXX-X'



.. _settings-navigation_enabled:

``NAVIGATION_ENABLED``
^^^^^^^^^^^^^^^^^^^^^^

Default: ``False`` 



.. _settings-navigation_brand:

``NAVIGATION_BRAND``
^^^^^^^^^^^^^^^^^^^^

Default: ``'Konfera'`` 



.. _settings-navigation_url:

``NAVIGATION_URL``
^^^^^^^^^^^^^^^^^^

Default: ``'/'`` 



.. _settings-navigation_logo:

``NAVIGATION_LOGO``
^^^^^^^^^^^^^^^^^^^

Default: ``None`` 

Application supports django-sitetree navigation support, weather it should be passed to template.



.. _settings-currency:

``CURRENCY``
^^^^^^^^^^^^

Default: ``('€', 'EUR')``

Currency used in the application. (Currently support just one currency). Defined as tuple of Currency Symbol (Unicode block) and  Currency code (ISO 4217)



.. _settings-talk_language:

``TALK_LANGUAGE``
^^^^^^^^^^^^^^^^^

Default: ``(('SK', _('Slovak')), ('CZ', _('Czech')), ('EN', _('English')),)``



.. _settings-language_default:

``TALK_LANGUAGE_DEFAULT``
^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``EN`` 



.. _settings-talk_duration:

``TALK_DURATION``
^^^^^^^^^^^^^^^^^

Default: ``((5, _('5 min')), (30, _('30 min')), (45, _('45 min')),)``



.. _settings-landing_page:

``LANDING_PAGE``
^^^^^^^^^^^^^^^^

Default: ``latest_conference`` 

Setting is a composite of two keywords: *<timewise>_<event>*
 * *<timewise>* can be: latest or earliest
 * *<event>* can be: conference or meetup

possible combinations: 
 * latest_conference (DEFAULT)
 * latest_meetup 
 * earliest_conference
 * earliest_meetup



.. _settings-order_redirect:

``ORDER_REDIRECT``
^^^^^^^^^^^^^^^^^^

Default: ``order_detail`` 

Specify url, where user will be redirected after registering the ticket.



.. _settings-register_email_notify:

``REGISTER_EMAIL_NOTIFY``
^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False`` 

Register email notification.



.. _settings-proposal_email_notify:

``PROPOSAL_EMAIL_NOTIFY``
^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False`` 

Notify after submitting proposal



.. _settings-email_notify_bcc:

``EMAIL_NOTIFY_BCC``
^^^^^^^^^^^^^^^^^^^^

Default value: ``[]`` 

Universal BCC for all notifications, MUST be empty list OR list of valid email adresses



.. _settings-unpaid_order_notification_repeat:

``UNPAID_ORDER_NOTIFICATION_REPEAT``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default value: ``3`` 

How many times we should repeat the email notification



.. _settings-unpaid_order_notification_repeat_delay:

``UNPAID_ORDER_NOTIFICATION_REPEAT_DELAY``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``5`` 

How long should we wait to notify about missing payment



.. _settings-site_url:

``SITE_URL``
^^^^^^^^^^^^

Default: ``'https://www.pycon.sk'`` 

Absolute url base with protocol, should not contain trailing slash (/) at the end



.. _settings-email_order_pdf_generation:

``ENABLE_ORDER_PDF_GENERATION``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False`` 

Enable ability to store order as PDF. In order to make this functionality work, make sure django-wkhtmltopdf, with wkhtmltopdf binary.
