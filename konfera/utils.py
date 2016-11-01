from konfera.settings import GOOGLE_ANALYTICS


def collect_view_data(request):
    """
    Function collects view_data generated by other functions
    """
    view_data = dict()

    if GOOGLE_ANALYTICS:
        view_data['ga'] = GOOGLE_ANALYTICS

    return view_data


def set_event_ga_to_context(event, context):
    if event.analytics:
        context['ga'] = event.analytics
