import logging

from datetime import datetime, timedelta
from smtplib import SMTPException
from wkhtmltopdf.views import PDFTemplateResponse
from subprocess import CalledProcessError

from django import VERSION
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import ModelFormMixin

from konfera import settings
from konfera.event.forms import SpeakerForm, TalkForm, ReceiptForm
from konfera.models.email_template import EmailTemplate
from konfera.models.event import Event
from konfera.models.talk import Talk
from konfera.models.ticket_type import TicketType
from konfera.models.order import Order
from konfera.utils import update_event_context, update_order_status_context

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

logger = logging.getLogger(__name__)


def event_venue_view(request, slug):
    event = get_object_or_404(Event.objects.published(), slug=slug)

    if not event.location or not event.location.get_here:
        raise Http404

    context = dict()
    context['venue'] = event.location.get_here
    update_event_context(event, context)

    return render(request=request, template_name='konfera/event/venue.html', context=context)


def event_sponsors_list_view(request, slug):
    event = get_object_or_404(Event.objects.published(), slug=slug)
    context = dict()
    update_event_context(event, context)

    return render(request=request, template_name='konfera/event/sponsors.html', context=context)


def event_speakers_list_view(request, slug):
    event = get_object_or_404(Event.objects.published(), slug=slug)
    context = dict()
    context['talks'] = event.talk_set.filter(status=Talk.APPROVED).order_by('primary_speaker__last_name')

    update_event_context(event, context)

    return render(request=request, template_name='konfera/event/speakers.html', context=context)


def event_details_view(request, slug):
    event = get_object_or_404(Event.objects.published(), slug=slug)
    context = dict()
    update_event_context(event, context)

    if event.event_type == Event.MEETUP:
        return render(request=request, template_name='konfera/event/details_meetup.html', context=context)

    return render(request=request, template_name='konfera/event/details_conference.html', context=context)


class CFPView(TemplateView):
    event = None
    template_name = 'konfera/event/cfp_form.html'
    message_text = _("Your talk proposal was successfully created.")

    def dispatch(self, *args, **kwargs):
        self.event = get_object_or_404(Event, slug=kwargs.get('slug'))

        if not self.event.cfp_allowed:
            raise Http404

        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        template = EmailTemplate.objects.get(name='confirm_proposal')

        if context['speaker_form'].is_valid() and context['talk_form'].is_valid():
            speaker = context['speaker_form'].save()
            talk_instance = context['talk_form'].save(commit=False)
            talk_instance.primary_speaker = speaker
            talk_instance.event = context['event']
            talk_instance.status = talk_instance.status or Talk.CFP
            talk_instance.save()

            if settings.PROPOSAL_EMAIL_NOTIFY:
                event_url = self.request.build_absolute_uri(reverse('event_details', args=[self.event.slug]))
                edit_url = self.request.build_absolute_uri(reverse('event_cfp_edit_form',
                                                                   args=[self.event.slug, talk_instance.uuid]))

                end_call = datetime.strftime(self.event.cfp_end, '%d %B %Y')

                subject = _('Proposal for {event} has been submitted'.format(event=self.event.title))
                template_data = {'first_name': speaker.first_name,
                                 'last_name': speaker.last_name,
                                 'event': self.event.title,
                                 'talk': talk_instance.title,
                                 'event_url': event_url,
                                 'edit_url': edit_url,
                                 'end_call': end_call}
                text_content = template.text_template.format(**template_data)
                html_content = template.html_template.format(**template_data)

                msg = EmailMultiAlternatives(subject, text_content, to=[speaker.email],
                                             bcc=settings.EMAIL_NOTIFY_BCC)
                msg.attach_alternative(html_content, "text/html")

                try:
                    msg.send()
                except SMTPException as e:
                    messages.success(self.request, _('Thank you for proposal submission.'))
                    messages.error(self.request, _('There was an error while sending email!\n'
                                                   'Copy this url to access the proposal details.'))
                    logger.critical('Sending proposal confirmation email raised an exception: %s', e)
                else:
                    template.add_count()
                    messages.success(self.request,
                                     _('Thank you for proposal submission, you will receive confirmation email soon.'))
            else:
                messages.success(self.request, self.message_text)

            return redirect('event_details', slug=context['event'].slug)

        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        update_event_context(self.event, context)

        context['speaker_form'] = SpeakerForm(self.request.POST or None, prefix='speaker')
        context['talk_form'] = TalkForm(self.request.POST or None, prefix='talk')

        return context


class CFPEditView(CFPView):
    message_text = _("Your talk proposal was successfully updated.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        talk = Talk.objects.get(uuid=context['uuid'])

        context['speaker_form'] = SpeakerForm(
            self.request.POST or None, instance=talk.primary_speaker, prefix='speaker')
        context['talk_form'] = TalkForm(self.request.POST or None, instance=talk, prefix='talk')

        return context

    def dispatch(self, *args, **kwargs):
        try:
            talk = Talk.objects.get(uuid=kwargs['uuid'])
        except (Talk.DoesNotExist, ValueError):
            raise Http404

        if talk.status not in [Talk.CFP, Talk.DRAFT]:
            raise Http404

        return super().dispatch(*args, **kwargs)


def schedule_redirect(request, slug):
    return redirect('schedule', slug=slug, day=0)


class ScheduleView(DetailView):
    model = Event
    template_name = 'konfera/event/schedule.html'

    def get_context_data(self, **kwargs):
        event = kwargs['object']

        context = super().get_context_data()
        context['day'] = int(self.kwargs['day'])

        date = event.date_from + timedelta(days=context['day'])
        context['schedule'] = event.schedules.filter(start__date=date.date()).order_by('room', 'start')

        event_duration = event.date_to - event.date_from
        context['interval'] = [
            {'day': day, 'date': event.date_from + timedelta(days=day)}
            for day in range(event_duration.days + 1)
        ]

        update_event_context(event, context)

        return context


def event_public_tickets(request, slug):
    event = get_object_or_404(Event.objects.published(), slug=slug)
    context = dict()
    update_event_context(event, context)

    available_tickets = event.tickettype_set.filter(accessibility=TicketType.PUBLIC)\
        .exclude(attendee_type=TicketType.AID).exclude(attendee_type=TicketType.VOLUNTEER)\
        .exclude(attendee_type=TicketType.PRESS)
    available_tickets = [t for t in available_tickets if t._get_current_status() == TicketType.ACTIVE]
    paginator = Paginator(available_tickets, 10)
    page = request.GET.get('page')

    try:
        available_tickets = paginator.page(page)
    except PageNotAnInteger:
        available_tickets = paginator.page(1)
    except EmptyPage:
        available_tickets = paginator.page(paginator.num_pages)

    context['tickets'] = available_tickets

    return render(request=request, template_name='konfera/event/public_tickets.html', context=context)


def event_about_us(request, slug):
    event = get_object_or_404(Event.objects.published(), slug=slug)
    context = dict()
    update_event_context(event, context)

    if not event.organizer:
        raise Http404(_('Organizer has not been set for event %s' % event.title))

    context['organizer'] = event.organizer

    return render(request=request, template_name='konfera/event/event_organizer.html', context=context)


class EventOrderDetailView(DetailView):
    model = Order
    template_name = 'konfera/order_details.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'order_uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['order'] = self.object
        context['allow_receipt_edit'] = True
        context['allow_pdf_storage'] = True

        if self.object.status != Order.AWAITING:
            context['allow_receipt_edit'] = False

        if self.object.event:
            update_event_context(self.object.event, context, show_sponsors=False)

        update_order_status_context(self.object.status, context)

        return context


class EventOrderDetailFormView(ModelFormMixin, EventOrderDetailView):
    form_class = ReceiptForm

    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()

        if self.object.status != Order.AWAITING:
            messages.error(self.request, _('You can not edit order. Please contact support.'))
            return redirect('order_details', order_uuid=self.object.uuid)

        return super().dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('order_details', kwargs={'order_uuid': self.object.order.uuid})

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['form'] = self.get_form()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'instance': self.object.receipt_of,
        })
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, _('Your order details has been updated.'))

        return super().form_valid(form)


class EventOrderDetailPDFView(EventOrderDetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['allow_receipt_edit'] = False
        context['allow_pdf_storage'] = False
        context['display_receipt'] = False

        if self.object.receipt_of.title:
            context['display_receipt'] = True

        return context

    def render_to_response(self, context):
        try:
            response = PDFTemplateResponse(request=self.request,
                                           template=self.template_name,
                                           filename="order-%s.pdf" % self.object.variable_symbol,
                                           context=self.get_context_data(),
                                           show_content_in_browser=False,
                                           cmd_options={'margin-top': 10,
                                                        "zoom": 1,
                                                        "viewport-size": "1366 x 513",
                                                        'javascript-delay': 1000,
                                                        'footer-center': '[page]/[topage]',
                                                        "no-stop-slow-scripts": True},
                                           )
        except CalledProcessError as e:
            logger.critical('Generating PDF Order detail raised an exception: %s', e)
            messages.error(self.request, _('Generating PDF Order detail failed. Please try again later.'))

            return redirect('order_details', order_uuid=self.object.uuid)

        return response
