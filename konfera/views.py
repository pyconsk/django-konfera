from django.shortcuts import render, get_object_or_404
from konfera.models import Event, Talk


def event_sponsors_list_view(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    sponsors = event.sponsors.all()

    context = {'event': event,
               'sponsors': sponsors,
               }

    return render(request=request,
                  template_name='konfera/event_sponsors.html',
                  context=context, )


def event_speakers_list_view(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    talks = event.talk_set.all().order_by('primary_speaker__last_name')

    context = {'event': event,
               'talks': talks,
               }

    return render(request=request,
                  template_name='konfera/event_speakers.html',
                  context=context, )
