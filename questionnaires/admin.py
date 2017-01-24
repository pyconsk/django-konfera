from django.contrib import admin

from dynamic_forms.admin import FormModelAdmin, FormModelDataAdmin
from dynamic_forms.models import FormModel, FormModelData

from .models import FormForTicket


@admin.register(FormForTicket)
class FormForTicketAdmin(admin.ModelAdmin):
    readonly_fields = ['form_data', 'ticket', 'date_created']
    list_display = ['ticket', 'form_data', 'date_created']
    search_fields = ['ticket__first_name', 'ticket__last_name', 'form_data__value']
    list_filter = ['ticket__type__event']


admin.site.unregister(FormModel)
admin.site.unregister(FormModelData)


class ProxyFormModel(FormModel):
    class Meta:
        proxy = True
        verbose_name = 'Questionnaire'
        verbose_name_plural = 'Questionnaires'


class ProxyFormModelDate(FormModelData):
    class Meta:
        proxy = True
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'


admin.site.register(ProxyFormModel, FormModelAdmin)
admin.site.register(ProxyFormModelDate, FormModelDataAdmin)
