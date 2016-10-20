from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from konfera.models.event import Event
from konfera.models.ticket import REQUESTED
from konfera.models.ticket_type import TicketType, VOLUNTEER, PUBLIC, PRIVATE, ACTIVE, PRESS, AID
from konfera.register.forms import RegistrationForm


def private_registration(request, event_slug, ticket_uuid):
    context = dict()
    event = get_object_or_404(Event, slug=event_slug)
    ticket_type = get_object_or_404(TicketType, event=event.id, uuid=ticket_uuid, accessibility=PRIVATE)
    if ticket_type.status != ACTIVE:
        messages.error(request, _('This ticket type is not available'))
        return redirect('event_details', event_slug)

    description_required = ticket_type in (VOLUNTEER, PRESS, AID)
    form = RegistrationForm(request.POST or None, description_required=description_required)

    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.status = REQUESTED
        new_ticket.type = ticket_type
        new_ticket.save()

        messages.success(request, _('Thanks for registering...'))

        return redirect('event_details', event_slug)

    context['form'] = form
    context['type'] = ticket_type.attendee_type

    return render(request, 'konfera/registration_form.html', context=context)


def register_volunteer(request, slug):
    context = dict()
    event = get_object_or_404(Event, slug=slug)
    volunteer_ticket_type = get_object_or_404(TicketType, event=event.id, attendee_type=VOLUNTEER,
                                              accessibility=PUBLIC)

    form = RegistrationForm(request.POST or None, description_required=True)

    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.status = REQUESTED
        new_ticket.type = volunteer_ticket_type
        new_ticket.save()

        messages.success(request, _('Thanks for registering...'))
        return redirect('event_details', slug)

    context['form'] = form
    context['type'] = VOLUNTEER

    return render(request, 'konfera/registration_form.html', context=context)
