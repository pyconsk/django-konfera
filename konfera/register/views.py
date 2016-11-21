from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse

from konfera.models.event import Event
from konfera.models.ticket import Ticket
from konfera.models.ticket_type import TicketType
from konfera.register.forms import RegistrationForm
from konfera import settings


def _register_ticket(request, event, ticket_type):
    context = dict()

    if ticket_type._get_current_status() != TicketType.ACTIVE:
        messages.error(request, _('This ticket type is not available'))

        return redirect('event_details', event.slug)

    description_required = ticket_type in (TicketType.VOLUNTEER, TicketType.PRESS, TicketType.AID)
    form = RegistrationForm(request.POST or None, description_required=description_required)

    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.status = Ticket.REQUESTED
        new_ticket.type = ticket_type
        new_ticket.save()

        if settings.REGISTER_EMAIL_NOTIFY:
            messages.success(request, _('Thank you for ordering ticket. You will receive confirmation email soon.'))

            event = new_ticket.type.event
            order_url = request.build_absolute_uri(reverse('order_details', args=[new_ticket.order.uuid]))
            event_url = request.build_absolute_uri(reverse('event_details', args=[event.slug]))
            subject = _('Your ticket for {event}.'.format(event=event.title))
            text_content = settings.REGISTER_EMAIL.format(first_name=new_ticket.first_name,
                                                          last_name=new_ticket.last_name,
                                                          event=event.title,
                                                          order_url=order_url,
                                                          event_url=event_url)
            html_content = settings.REGISTER_EMAIL_HTML.format(first_name=new_ticket.first_name,
                                                               last_name=new_ticket.last_name,
                                                               event=event.title,
                                                               order_url=order_url,
                                                               event_url=event_url)
            msg = EmailMultiAlternatives(subject, text_content, to=[new_ticket.email], bcc=settings.REGISTER_EMAIL_BCC)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        else:
            messages.success(request, _('Thank you for ordering ticket.'))

        return redirect('order_details', new_ticket.order.uuid)

    context['form'] = form
    context['type'] = ticket_type.attendee_type

    return render(request, 'konfera/registration_form.html', context=context)


def register_ticket(request, slug, ticket_uuid):
    event = get_object_or_404(Event, slug=slug)
    ticket_type = get_object_or_404(TicketType, event=event, uuid=ticket_uuid)

    return _register_ticket(request, event, ticket_type)


def _register_ticket_attendee(request, slug, attendee_type):
    event = get_object_or_404(Event, slug=slug)
    ticket_types = TicketType.objects.filter(event=event, attendee_type=attendee_type)

    if ticket_types and len(ticket_types) == 1 and ticket_types[0].status == TicketType.STATUSES[TicketType.ACTIVE]:
        return _register_ticket(request, event, ticket_types[0])
    else:
        messages.warning(request, _('The ticket type is not available!'))
        return redirect('event_tickets', slug)


def register_ticket_volunteer(request, slug):
    return _register_ticket_attendee(request, slug, TicketType.VOLUNTEER)


def register_ticket_press(request, slug):
    return _register_ticket_attendee(request, slug, TicketType.PRESS)


def register_ticket_aid(request, slug):
    return _register_ticket_attendee(request, slug, TicketType.AID)
