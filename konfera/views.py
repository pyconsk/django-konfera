from django.shortcuts import render, get_object_or_404
from konfera.models import Event, Sponsor


def sponsor_list_view(request, event_slug):
    event = get_object_or_404(Event, slug=event_slug)
    sponsors = Sponsor.objects.select_related('event') \
                    .filter(event=event).order_by('type')

    context = {'event': event,
               'sponsors': sponsors, }
    template = 'konfera/event_sponsors.html'

    return render(request=request,
                  template_name=template,
                  context=context, )
