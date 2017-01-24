from django.shortcuts import get_object_or_404, render

from dynamic_forms.actions import dynamic_form_store_database
from dynamic_forms.models import FormModel
from dynamic_forms.views import DynamicFormView

from konfera.models import Ticket

from .models import FormForTicket


class ShowFormForTicket(DynamicFormView):

    def get_template_names(self):
        return ['questionnaires/form.html']

    def get_data(self):
        if 'model' not in self.kwargs:
            self.kwargs['model'] = get_object_or_404(FormModel, pk=self.kwargs['pk'])
        if 'ticket' not in self.kwargs:
            self.kwargs['ticket'] = get_object_or_404(Ticket, uuid=self.kwargs['ticket_uuid'])

    def get_success_url(self):
        return self.request.path

    def dispatch(self, request, *args, **kwargs):
        self.get_data()

        if FormForTicket.objects.filter(form_data__form=self.kwargs['model'], ticket=self.kwargs['ticket']).exists():
            return render(request, 'questionnaires/form_already_submited.html')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.get_data()
        data = dynamic_form_store_database(self.kwargs['model'], form, self.request)
        FormForTicket.objects.create(form_data=data, ticket=self.kwargs['ticket'])
        return super().form_valid(form)
