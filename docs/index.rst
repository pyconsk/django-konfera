.. django-konfera documentation master file, created by
   sphinx-quickstart on Sat Jan 21 15:17:01 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-konfera's documentation!
==========================================

Contents:

.. toctree::
   :maxdepth: 2

   installation
   contributing
   options
   talks

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Attendee Check In
=================

1. Create a group in admin, called *Checkin*.
2. Add the users who should be able to access the check-in system to the group.

The users in *Checkin* group can now access the check-in system at `/event_slug/checkin/`.

In the check-in system, you can use the search for either *First name*, *Last name* or *Email*. However, not all at once.
