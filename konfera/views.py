from django.views.generic import ListView

from konfera.models.event import Event


class EventsByTypeListView(ListView):
    event_type = None
    queryset = Event.objects.all()
    paginate_by = 5

    def get_queryset(self):
        queryset = self.queryset
        if self.event_type is not None:
            queryset = queryset.filter(event_type=self.event_type)
        return queryset
