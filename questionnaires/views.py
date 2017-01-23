from django.shortcuts import get_object_or_404
from django.http import Http404

from dynamic_forms.models import FormModel
from dynamic_forms.views import DynamicFormView

from konfera.models import Ticket

from .models import FormForTicket


class ShowFormForTicket(DynamicFormView):

    def dispatch(self, request, *args, **kwargs):
        form_model = get_object_or_404(FormModel, pk=kwargs['pk'])

        self.kwargs['model'] = form_model
        self.kwargs['ticket'] = get_object_or_404(Ticket, uuid=kwargs['ticket_uuid'])

        if FormForTicket.objects.filter(form_data__form=form_model, ticket=self.kwargs['ticket']).exists():
            raise Http404  # todo: show a better error

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        # todo: this is not invoked?!
        response = super().form_valid(form)
        print('I am invoked!\n' * 10)

        FormForTicket.objects.create(form=form.instance, ticket=self.kwargs['ticket'])

        return response
