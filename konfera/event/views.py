from datetime import timedelta

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView

from konfera.event.forms import SpeakerForm, TalkForm
from konfera.models.event import Event
from konfera.models.sponsor import Sponsor
from konfera.models.talk import Talk
from konfera.models.ticket_type import TicketType
from konfera.models.order import Order
from konfera.utils import set_event_ga_to_context


def event_venue_view(request, slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=slug)
    if not event.location or not event.location.get_here:
        raise Http404

    context['event'] = event
    context['venue'] = event.location.get_here

    set_event_ga_to_context(event, context)

    return render(request=request, template_name='konfera/event_venue.html', context=context)


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
    context['talks'] = event.talk_set.filter(status=Talk.APPROVED).order_by('primary_speaker__last_name')

    set_event_ga_to_context(event, context)

    return render(request=request, template_name='konfera/event_speakers.html', context=context)


def event_details_view(request, slug):
    context = dict()

    event = get_object_or_404(Event.objects.published(), slug=slug)
    context['event'] = event
    context['sponsors'] = event.sponsors.filter(type__in=(Sponsor.PLATINUM, Sponsor.GOLD, Sponsor.SILVER))

    set_event_ga_to_context(event, context)

    if event.event_type == Event.MEETUP:
        return render(request=request, template_name='konfera/event/details_meetup.html', context=context)

    return render(request=request, template_name='konfera/event/details_conference.html', context=context)


class CFPView(TemplateView):
    template_name = 'konfera/event/cfp_form.html'
    message_text = _("Your talk proposal was successfully created.")

    def dispatch(self, *args, **kwargs):
        event = get_object_or_404(Event, slug=kwargs.get('slug'))

        if not event.cfp_allowed:
            raise Http404

        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if context['speaker_form'].is_valid() and context['talk_form'].is_valid():
            speaker_instance = context['speaker_form'].save()
            talk_instance = context['talk_form'].save(commit=False)
            talk_instance.primary_speaker = speaker_instance
            talk_instance.event = context['event']
            talk_instance.status = talk_instance.status or Talk.CFP
            talk_instance.save()
            messages.success(self.request, self.message_text)

            return redirect('event_details', slug=context['event'].slug)

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['event'] = event = Event.objects.get(slug=kwargs['slug'])
        context['sponsors'] = event.sponsors.filter(type__in=(Sponsor.PLATINUM, Sponsor.GOLD, Sponsor.SILVER))

        context['speaker_form'] = SpeakerForm(self.request.POST or None, prefix='speaker')
        context['talk_form'] = TalkForm(self.request.POST or None, prefix='talk')

        set_event_ga_to_context(event, context)

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

        if talk.status not in [Talk.CFP, Talk.DRAFT]:
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
    available_tickets = event.tickettype_set.filter(accessibility=TicketType.PUBLIC)\
        .exclude(attendee_type=TicketType.AID).exclude(attendee_type=TicketType.VOLUNTEER)\
        .exclude(attendee_type=TicketType.PRESS)
    available_tickets = [t for t in available_tickets if t._get_current_status() == TicketType.ACTIVE]
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


def event_order_detail(request, order_uuid):
    context = dict()
    order = get_object_or_404(Order, uuid=order_uuid)
    context['order'] = order
    if order.status == Order.PAID:
        context['status_label'] = 'label-success'
    elif order.status in [Order.CANCELLED, Order.EXPIRED]:
        context['status_label'] = 'label-danger'
    else:
        context['status_label'] = 'label-warning'
    return render(request=request, template_name='konfera/order_details.html', context=context)
