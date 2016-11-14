from django.contrib import admin

from .models import ProcessedTransaction


class ProcessedTransactionAdmin(admin.ModelAdmin):
    readonly_fields = ('transaction_id', 'variable_symbol', 'amount', 'date', 'currency', 'executor', 'comment')
    list_display = ('transaction_id', 'executor', 'amount')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(ProcessedTransaction, ProcessedTransactionAdmin)
