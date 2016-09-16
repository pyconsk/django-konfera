from django.shortcuts import render, get_object_or_404
from konfera.models import Event


def sponsor_list_view(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    sponsors = event.sponsors.all()

    context = {'event': event,
               'sponsors': sponsors,
               }

    return render(request=request,
                  template_name='konfera/event_sponsors.html',
                  context=context, )
