from django.shortcuts import redirect
from django.views.generic import ListView
from django.shortcuts import render
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from konfera.models.event import Event
from konfera.settings import LANDING_PAGE


def index(request):
    try:
        timewise, event_type = LANDING_PAGE.split('_')
        timewise = timewise.lower()
        event_type = event_type.upper()
    except BaseException as be:
        raise (_('%s\nIncorrect LANDING_PAGE setting, need latest|earliest_conference|meetup', be))

    events = Event.objects.published().filter(event_type=getattr(Event, event_type))
    selected_event = getattr(events, timewise)('date_from')
    if not selected_event:
        messages.info(request, _('No %s event has been found. Redirected to default list.' % event_type))
        return render(request=request, template_name='konfera/list_events.html')

    return redirect('event_details', slug=selected_event.slug)


class EventsByTypeListView(ListView):
    event_type = None
    queryset = Event.objects.all()
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.count() == 1:
            return redirect('event_details', slug=queryset[0].slug)

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset

        if self.event_type is not None:
            queryset = queryset.filter(event_type=self.event_type)

        return queryset


class EventsListView(EventsByTypeListView):
    template_name = 'konfera/list_events.html'


class MeetupsListView(EventsByTypeListView):
    paginate_by = 15
    event_type = Event.MEETUP
    template_name = 'konfera/list_meetups.html'


class ConferencesListView(EventsByTypeListView):
    event_type = Event.CONFERENCE
    template_name = 'konfera/list_conferences.html'
