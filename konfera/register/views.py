from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from konfera.models.event import Event, MEETUP
from konfera.models.ticket import REQUESTED
from konfera.models.ticket_type import TicketType, VOLUNTEER
from konfera.register.forms import VolunteerRegistrationForm


def register_volunteer(request, slug):
    context = dict()
    event = get_object_or_404(Event, slug=slug)
    volunteer_ticket_type = get_object_or_404(TicketType, event=event.id, attendee_type=VOLUNTEER)

    if request.method == "POST":
        form = VolunteerRegistrationForm(request.POST)

        if form.is_valid():
            new_ticket = form.save(commit=False)
            new_ticket.status = REQUESTED
            new_ticket.type = volunteer_ticket_type
            new_ticket.save()

            if volunteer_ticket_type.accessibility != 'public':
                volunteer_ticket_type.accessibility = 'public'
                volunteer_ticket_type.save()

            return redirect('event_details', slug)
    else:
        form = VolunteerRegistrationForm()

    context['form'] = form
    context['type'] = VOLUNTEER

    return render(request, 'konfera/registration_form.html', context=context)


def meetup_list(request):
    meetups = Event.objects.filter(event_type=MEETUP).order_by('date_from')
    context = dict()

    if meetups.count() == 1:
        return redirect('meetup_detail', event_slug=meetups[0].slug)

    paginator = Paginator(meetups, 5)
    page = request.GET.get('page')

    try:
        meetups = paginator.page(page)
    except PageNotAnInteger:
        meetups = paginator.page(1)
    except EmptyPage:
        meetups = paginator.page(paginator.num_pages)

    context['meetups'] = meetups

    return render(request, 'konfera/meetups.html', context=context)
