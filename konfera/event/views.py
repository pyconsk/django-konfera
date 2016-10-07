from datetime import timedelta

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.utils.translation import ugettext_lazy as _

from konfera.event.forms import SpeakerForm, TalkForm
from konfera.forms import VolunteerRegistrationForm
from konfera.models.event import Event
from konfera.models.talk import APPROVED, CFP
from konfera.models.ticket import REQUESTED
from konfera.models.ticket_type import TicketType, VOLUNTEER


def event_sponsors_list_view(request, event_slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=event_slug)
    context['event'] = event
    context['sponsors'] = event.sponsors.all().order_by('type', 'title')

    return render(request=request, template_name='konfera/event_sponsors.html', context=context)


def event_speakers_list_view(request, event_slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=event_slug)
    context['event'] = event
    context['talks'] = event.talk_set.filter(status=APPROVED).order_by('primary_speaker__last_name')

    return render(request=request, template_name='konfera/event_speakers.html', context=context)


def event_list(request):
    context = dict()

    events = Event.objects.published().order_by('date_from')

    if events.count() == 1:
        return redirect('event_details', event_slug=events[0].slug)

    paginator = Paginator(events, 10)
    page = request.GET.get('page')

    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)

    context['events'] = events

    return render(request=request, template_name='konfera/events.html', context=context)


def event_details_view(request, event_slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=event_slug)
    context['event'] = event
    context['sponsors'] = event.sponsors.all()

    return render(request=request, template_name='konfera/event_details.html', context=context)


def cfp_form_view(request, event_slug):
    context = dict()
    speaker_form = SpeakerForm(request.POST or None, prefix='speaker')
    talk_form = TalkForm(request.POST or None, prefix='talk')

    if speaker_form.is_valid() and talk_form.is_valid():
        speaker_instance = speaker_form.save()
        talk_instance = talk_form.save(commit=False)
        talk_instance.primary_speaker = speaker_instance
        talk_instance.status = CFP
        talk_instance.event = Event.objects.get(slug=event_slug)
        talk_instance.save()
        message_text = _("Your talk proposal successfully created")
        messages.success(request, message_text)

        return HttpResponseRedirect(redirect_to='/event/')

    context['speaker_form'] = speaker_form
    context['talk_form'] = talk_form

    return render(request=request, template_name='konfera/cfp_form.html', context=context)


def schedule_redirect(request, slug):
    return redirect('schedule', slug=slug, day=0)


class ScheduleView(DetailView):
    model = Event
    template_name = 'konfera/event_schedule.html'

    def get_context_data(self, **kwargs):
        event = kwargs['object']

        context = super().get_context_data()
        context['day'] = int(self.kwargs['day'])

        date = event.date_from + timedelta(days=context['day'])
        context['schedule'] = event.schedules.filter(start__date=date.date()).order_by('room', 'start')

        event_duration = event.date_to - event.date_from
        context['interval'] = [
            {'day': day, 'date': event.date_from + timedelta(days=day)}
            for day in range(event_duration.days + 1)
        ]

        return context
