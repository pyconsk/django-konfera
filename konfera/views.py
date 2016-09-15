from django.shortcuts import render, get_object_or_404
from konfera.models import Event, Sponsor


def sponsor_list_view(request, event_id):
    sponsors = Sponsor.objects.select_related('event') \
                    .filter(event__id=event_id).order_by('type')
    event = Event.objects.get(pk=event_id)
    context = {'event': event,
               'sponsors': sponsors,
               }

    return render(request=request,
                  template_name='konfera/event_sponsors.html',
                  context=context)
