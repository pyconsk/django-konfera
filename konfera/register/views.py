import logging
from smtplib import SMTPException

from django import VERSION
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives

from konfera.models.email_template import EmailTemplate
from konfera.models.sponsor import Sponsor
from konfera.models.event import Event
from konfera.models.ticket import Ticket
from konfera.models.ticket_type import TicketType
from konfera.register.forms import RegistrationForm
from konfera import settings

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

logger = logging.getLogger(__name__)


def _register_ticket(request, event, ticket_type):
    context = dict()
    template = EmailTemplate.objects.get(name='register_email')

    if ticket_type._get_current_status() != TicketType.ACTIVE:
        messages.error(request, _('This ticket type is not available'))

        return redirect('event_details', event.slug)

    description_required = ticket_type.attendee_type in (TicketType.VOLUNTEER, TicketType.PRESS, TicketType.AID)
    form = RegistrationForm(request.POST or None, description_required=description_required)

    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.status = Ticket.REQUESTED
        new_ticket.type = ticket_type
        new_ticket.save()

        if settings.REGISTER_EMAIL_NOTIFY:

            event = new_ticket.type.event
            order_url = request.build_absolute_uri(reverse('order_details', args=[new_ticket.order.uuid]))
            event_url = request.build_absolute_uri(reverse('event_details', args=[event.slug]))
            subject = _('Your ticket for {event}.'.format(event=event.title))
            text_content = template.text_template.format(first_name=new_ticket.first_name,
                                                         last_name=new_ticket.last_name,
                                                         event=event.title,
                                                         order_url=order_url,
                                                         event_url=event_url)
            html_content = template.html_template.format(first_name=new_ticket.first_name,
                                                         last_name=new_ticket.last_name,
                                                         event=event.title,
                                                         order_url=order_url,
                                                         event_url=event_url)
            msg = EmailMultiAlternatives(subject, text_content, to=[new_ticket.email], bcc=settings.EMAIL_NOTIFY_BCC)
            msg.attach_alternative(html_content, "text/html")

            try:
                msg.send()
            except SMTPException as e:
                messages.success(request, _('Thank you for ordering ticket.'))
                messages.error(request, _('There was an error while sending email! Copy this url, to access this order\
                                           again.'))
                logger.critical('Sending email raised an exception: %s', e)
            else:
                # increase count on email_template
                template.add_count()
                messages.success(request, _('Thank you for ordering ticket. You\'ll receive confirmation email soon.'))

        else:
            messages.success(request, _('Thank you for ordering ticket.'))

        return redirect(settings.ORDER_REDIRECT, new_ticket.order.uuid)

    context['event'] = event
    context['sponsors'] = event.sponsors.filter(type__in=(Sponsor.PLATINUM, Sponsor.GOLD, Sponsor.SILVER))
    context['form'] = form
    context['type'] = ticket_type.attendee_type

    return render(request, 'konfera/registration_form.html', context=context)


def register_ticket_uuid(request, slug, ticket_uuid):
    event = get_object_or_404(Event, slug=slug)
    ticket_type = get_object_or_404(TicketType, event=event, uuid=ticket_uuid)

    return _register_ticket(request, event, ticket_type)


def _pre_process_ticket_registration(request, slug, attendee_type):
    event = get_object_or_404(Event, slug=slug)
    ticket_type = get_object_or_404(TicketType, event=event, attendee_type=attendee_type)

    return _register_ticket(request, event, ticket_type)


def register_ticket_volunteer(request, slug):
    return _pre_process_ticket_registration(request, slug, TicketType.VOLUNTEER)


def register_ticket_press(request, slug):
    return _pre_process_ticket_registration(request, slug, TicketType.PRESS)


def register_ticket_aid(request, slug):
    return _pre_process_ticket_registration(request, slug, TicketType.AID)
