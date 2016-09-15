from django.shortcuts import render
from konfera.models import Event, Sponsor


def sponsor_list_view(request):
    events = Event.objects.all()
    sponsors = Sponsor.objects.all()
    context = {'events': events,
               'sponsors': sponsors,
               }

    return render(request=request,
                  template_name='konfera/sponsors_per_event.html',
                  context=context)
