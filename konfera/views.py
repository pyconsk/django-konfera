from django.shortcuts import redirect
from django.views.generic import ListView

from konfera.models.event import Event, MEETUP, CONFERENCE


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
    event_type = MEETUP
    template_name = 'konfera/list_meetups.html'


class ConferencesListView(EventsByTypeListView):
    event_type = CONFERENCE
    template_name = 'konfera/list_conferences.html'
