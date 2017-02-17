import logging
from smtplib import SMTPException

from django import VERSION
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from konfera import settings
from konfera.models.sponsor import Sponsor
from konfera.models.event import Event
from konfera.models.ticket import Ticket
from konfera.models.ticket_type import TicketType
from konfera.register.forms import RegistrationForm
from konfera.utils import send_email

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

logger = logging.getLogger(__name__)


def _register_ticket(request, event, ticket_type):
    context = dict()
    template_name = 'register_email'

    if ticket_type._get_current_status() != TicketType.ACTIVE:
        messages.error(request, _('This ticket type is not available'), extra_tags='danger')

        return redirect('event_details', event.slug)

    description_required = ticket_type.attendee_type in (TicketType.VOLUNTEER, TicketType.PRESS, TicketType.AID)
    form = RegistrationForm(request.POST or None, initial={'type': ticket_type.pk},
                            description_required=description_required)

    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.status = Ticket.REQUESTED
        new_ticket.save()

        if settings.REGISTER_EMAIL_NOTIFY:

            event = new_ticket.type.event
            order_url = request.build_absolute_uri(reverse('order_detail', args=[new_ticket.order.uuid]))
            event_url = request.build_absolute_uri(reverse('event_details', args=[event.slug]))
            subject = _('Your ticket for {event}.'.format(event=event.title))
            formatting_dict = {
                'first_name': new_ticket.first_name,
                'last_name': new_ticket.last_name,
                'event': event.title,
                'order_url': order_url,
                'event_url': event_url,
            }
            addresses = {'to': [new_ticket.email]}
            send_email(addresses, subject, template_name, formatting_dict=formatting_dict)
            messages.success(request, _('Thank you for ordering ticket. You\'ll receive confirmation email soon.'))
        else:
            messages.success(request, _('Thank you for ordering ticket.'))

        return redirect(settings.ORDER_REDIRECT, new_ticket.order.uuid)

    context['event'] = event
    context['sponsors'] = event.sponsors.filter(type__in=(Sponsor.PLATINUM, Sponsor.GOLD, Sponsor.SILVER))
    context['form'] = form
    context['title'] = ticket_type.title
    context['type'] = ticket_type.attendee_type
    context['price'] = ticket_type.price
    context['description'] = ticket_type.description

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
