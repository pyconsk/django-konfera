from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from konfera.models.event import Event, MEETUP

def meetup_list(request):
    meetups = Event.objects.filter(event_type=MEETUP).order_by('date_from').reverse()
    context = dict()

    if meetups.count() == 1:
        return redirect('meetup_detail', event_slug=meetups[0].slug)

    paginator = Paginator(meetups, 5)
    page = request.GET.get('page')

    try:
        meetups = paginator.page(page)
    except PageNotAnInteger:
        meetups = paginator.page(1)
    except EmptyPage:
        meetups = paginator.page(paginator.num_pages)

    context['meetups'] = meetups

    return render(request, 'konfera/meetups.html', context=context)
