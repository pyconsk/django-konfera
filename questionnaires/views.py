from django.shortcuts import get_object_or_404
from django.http import Http404

from dynamic_forms.actions import dynamic_form_store_database
from dynamic_forms.views import DynamicFormView

from konfera.models import Ticket

from .models import FormForTicket, QuestionnaireForEvent


class ShowFormForTicket(DynamicFormView):

    def get_template_names(self):
        return ['questionnaires/form.html']

    def get_data(self):
        if 'ticket' not in self.kwargs:
            self.kwargs['ticket'] = get_object_or_404(Ticket, uuid=self.kwargs['ticket_uuid'])
        if 'model' not in self.kwargs:
            print(QuestionnaireForEvent.objects.active(self.kwargs['ticket'].type.event))
            questionnaire = get_object_or_404(
                QuestionnaireForEvent.objects.active(self.kwargs['ticket'].type.event),
                pk=self.kwargs['pk']
            )
            self.kwargs['model'] = questionnaire.questionnaire

    def dispatch(self, request, *args, **kwargs):
        self.get_data()

        if FormForTicket.objects.filter(form_data__form=self.kwargs['model'], ticket=self.kwargs['ticket']).exists():
            raise Http404  # todo: show a better error

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.get_data()
        data = dynamic_form_store_database(self.kwargs['model'], form, self.request)
        FormForTicket.objects.create(form_data=data, ticket=self.kwargs['ticket'])
        return super().form_valid(form)
