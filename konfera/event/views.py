from datetime import timedelta

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from konfera.event.forms import SpeakerForm, TalkForm
from konfera.models.event import Event, MEETUP
from konfera.models.sponsor import PLATINUM, GOLD, SILVER
from konfera.models.talk import APPROVED, CFP, DRAFT, Talk
from konfera.models.ticket_type import PUBLIC, ACTIVE, PRESS, AID, VOLUNTEER
from konfera.utils import set_event_ga_to_context


def event_sponsors_list_view(request, slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=slug)
    context['event'] = event
    context['sponsors'] = event.sponsors.all().order_by('type', 'title')

    set_event_ga_to_context(event, context)

    return render(request=request, template_name='konfera/event_sponsors.html', context=context)


def event_speakers_list_view(request, slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=slug)
    context['event'] = event
    context['talks'] = event.talk_set.filter(status=APPROVED).order_by('primary_speaker__last_name')

    set_event_ga_to_context(event, context)

    return render(request=request, template_name='konfera/event_speakers.html', context=context)


def event_details_view(request, slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=slug)
    context['event'] = event
    context['sponsors'] = event.sponsors.filter(type__in=(PLATINUM, GOLD, SILVER))

    set_event_ga_to_context(event, context)

    if event.event_type == MEETUP:
        return render(request=request, template_name='konfera/event/details_meetup.html', context=context)

    return render(request=request, template_name='konfera/event/details_conference.html', context=context)


class CFPView(TemplateView):
    template_name = 'konfera/cfp_form.html'
    message_text = _("Your talk proposal was successfully created.")

    def dispatch(self, *args, **kwargs):
        if not Event.objects.filter(slug=kwargs.get('slug')).exists():
            raise Http404
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if context['speaker_form'].is_valid() and context['talk_form'].is_valid():
            speaker_instance = context['speaker_form'].save()
            talk_instance = context['talk_form'].save(commit=False)
            talk_instance.primary_speaker = speaker_instance
            talk_instance.event = context['event']
            talk_instance.status = talk_instance.status or CFP
            talk_instance.save()
            messages.success(self.request, self.message_text)

            return redirect('event_details', slug=context['event'].slug)

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['event'] = Event.objects.get(slug=kwargs['slug'])
        context['speaker_form'] = SpeakerForm(self.request.POST or None, prefix='speaker')
        context['talk_form'] = TalkForm(self.request.POST or None, prefix='talk')

        set_event_ga_to_context(context['event'], context)

        return context


class CFPEditView(CFPView):
    message_text = _("Your talk proposal was successfully updated.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        talk = Talk.objects.get(uuid=context['uuid'])

        context['speaker_form'] = SpeakerForm(
            self.request.POST or None, instance=talk.primary_speaker, prefix='speaker')
        context['talk_form'] = TalkForm(self.request.POST or None, instance=talk, prefix='talk')

        return context

    def dispatch(self, *args, **kwargs):
        try:
            talk = Talk.objects.get(uuid=kwargs['uuid'])
        except (Talk.DoesNotExist, ValueError):
            raise Http404

        if talk.status not in [CFP, DRAFT]:
            raise Http404

        return super().dispatch(*args, **kwargs)


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

        set_event_ga_to_context(event, context)

        return context


def event_public_tickets(request, slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=slug)
    context['event'] = event
    available_tickets = event.tickettype_set.filter(accessibility=PUBLIC).exclude(attendee_type=AID)\
        .exclude(attendee_type=VOLUNTEER).exclude(attendee_type=PRESS)
    available_tickets = [t for t in available_tickets if t._get_current_status() == ACTIVE]
    paginator = Paginator(available_tickets, 10)
    page = request.GET.get('page')

    try:
        available_tickets = paginator.page(page)
    except PageNotAnInteger:
        available_tickets = paginator.page(1)
    except EmptyPage:
        available_tickets = paginator.page(paginator.num_pages)

    context['tickets'] = available_tickets
    return render(request=request, template_name='konfera/event_public_tickets.html', context=context)
