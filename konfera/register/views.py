from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages

from konfera.models.event import Event
from konfera.models.ticket import REQUESTED
from konfera.models.ticket_type import TicketType, VOLUNTEER, PUBLIC
from konfera.register.forms import VolunteerRegistrationForm


def register_volunteer(request, slug):
    context = dict()
    event = get_object_or_404(Event, slug=slug)
    volunteer_ticket_type = get_object_or_404(TicketType, event=event.id, attendee_type=VOLUNTEER,
                                              accessibility=PUBLIC)

    form = VolunteerRegistrationForm(request.POST or None)

    if form.is_valid():
        new_ticket = form.save(commit=False)
        new_ticket.status = REQUESTED
        new_ticket.type = volunteer_ticket_type
        new_ticket.save()

        message_text = ("Thanks for registering...")
        messages.success(request, message_text)

        return redirect('event_details', slug)
    else:
        form = VolunteerRegistrationForm()

    context['form'] = form
    context['type'] = VOLUNTEER

    return render(request, 'konfera/registration_form.html', context=context)
