from django.db import models
from django.core.validators import ValidationError
from django.utils.translation import ugettext as _

from konfera.models.abstract import KonferaModel


class FormForTicket(KonferaModel, models.Model):
    form_data = models.ForeignKey('dynamic_forms.FormModelData', on_delete=models.CASCADE)
    ticket = models.ForeignKey('konfera.Ticket', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        if FormForTicket.objects.filter(form_data__form=self.form_data.form, ticket=self.ticket).exists():
            raise ValidationError(_('Form already submitted.'))
        super().clean()

    class Meta:
        verbose_name = 'Answer for a ticket'
        verbose_name_plural = 'Answers for tickets'
