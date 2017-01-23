from django.contrib import admin

from .models import FormForTicket


@admin.register(FormForTicket)
class FormForTicketAdmin(admin.ModelAdmin):
    readonly_fields = ['form_data', 'ticket', 'date_created']
    list_display = ['ticket', 'form_data', 'date_created']
    search_fields = ['ticket__first_name', 'ticket__last_name', 'form_data__value']
    list_filter = ['ticket__type__event']
