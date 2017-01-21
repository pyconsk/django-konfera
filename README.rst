django-konfera
==============

.. image:: https://badges.gitter.im/pyconsk/django-konfera.svg
    :target: https://gitter.im/pyconsk/django-konfera?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://travis-ci.org/pyconsk/django-konfera.png?branch=master
    :target: https://travis-ci.org/pyconsk/django-konfera

.. image:: https://codecov.io/gh/pyconsk/django-konfera/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/pyconsk/django-konfera

.. image:: https://readthedocs.org/projects/django-konfera/badge/
    :target: https://django-konfera.readthedocs.io/en/latest/


Yet another event organization app for Django.
----------------------------------------------

Web application written in python (django) to manage event organization.

Features in application (for version 0.1)

* store multiple Events (conferences, meetups) via admin area
* manage Sponsors, Speakers (and talks, or workshops) per event via admin area
* manage schedule via admin area
* manage orders via admin area
* call for proposals (speaker and talk registration)
* volunteer registration
* show event details (speakers, sponsors)

Work to be done in near future

* attendees registration (tickets)
* order details (receipts) in frontend
* schedule generation in ics calendar format
* automated payments processing (PayPal, FIO bank)
* attendees registration on premise

Quick start
-----------

There is example directory, that provides a convenience feature to allow potential users to try the app straight from the app repo without having to create a django project. It can also be used to develop the app in place. You can read more in `README.md <https://github.com/pyconsk/django-konfera/blob/master/example/README.md>`_ inside example directory.

Contributing Guide
------------------

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given. For more details see file: `docs/contributing.rst <https://github.com/pyconsk/django-konfera/blob/master/docs/contributing.rst>`_

Disclaimer
----------

Django-konfera was designed for `Bratislava Python Meetups <https://pycon.sk/sk/meetup.html#github>`_ as a workshop, where people are learning Django and will be user for `PyCon SK 2017 <https://pycon.sk#github>`_ organization.
