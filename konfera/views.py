from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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


def event_list(request):
    events = Event.objects.all().order_by('date_from')
    paginator = Paginator(events, 10)
    page = request.GET.get('page')
    try:
        events = paginator.page(page)
    except PageNotAnInteger:
        events = paginator.page(1)
    except EmptyPage:
        events = paginator.page(paginator.num_pages)
    context = {'events': events}
    return render(request=request,
                  template_name='konfera/events.html',
                  context=context)
