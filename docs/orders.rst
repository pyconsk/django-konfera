Orders
======

Once user decide to visit event, ha can register ticket, which create order. Order has to paid in order to be valid ticket.

Order statuses:
* *Awaiting payment* - Newly created order that hasnt been paid off yet. *Default* status for all new orders.
* *Paid* - Order has been paid for, or if it is grant, it has been approved.
* *Partly Paid* - Order has been paid for, but the amount of received money was less that the price.
* *Expired* - Order hasn't been paid for a long time and it has expired.
* *Cancelled* - Order was voided by user.

Management commands
-------------------

Orders can be managed by projects `manage.py` commands.

* *show_overdue_orders* - Management command will just show orders, that are overdue (after due date with enaought notifications) and will be expired on next run of command *email_unpaid_notifications* 
* *show_unpaid_orders* - Management command will just show orders, that are not paid and are after due date, or last notification is after due date and user will be notified on next run of command *email_unpaid_notifications*
* *email_unpaid_notifications* - Management command will send notifications, to orders that were set to expired, and also will notify orders that after due date, or last notification is after due date.

Sample command ::

    $ ./manage.py email_unpaid_notifications

