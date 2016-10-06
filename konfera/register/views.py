from django.shortcuts import render, get_object_or_404, redirect
from konfera.models import Event, TicketType
from konfera.models.ticket_type import VOLUNTEER
from konfera.register.forms import VolunteerRegistrationForm
from konfera.models.ticket import REQUESTED

# Create your views here.

def register_volunteer(request, event_slug):
    context = dict()
    event = get_object_or_404(Event, slug=event_slug)
    volunteer_ticket_type = get_object_or_404(TicketType, event=event.id, attendee_type=VOLUNTEER)

    if request.method == "POST":
        form = VolunteerRegistrationForm(request.POST)

        if form.is_valid():
            new_ticket = form.save(commit=False)
            new_ticket.status = REQUESTED
            new_ticket.type = volunteer_ticket_type
            new_ticket.save()

            return redirect('event_details', event_slug)
    else:
        form = VolunteerRegistrationForm()

    context['form'] = form
    context['type'] = VOLUNTEER

    return render(request, 'konfera/registration_form.html', context=context)
