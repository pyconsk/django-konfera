from django.db import models
from django.core.validators import ValidationError
from django.utils import timezone
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

    def __str__(self):
        return '{} - {}'.format(self.form_data.form.name, self.ticket)

    class Meta:
        verbose_name = _('Answer for a ticket')
        verbose_name_plural = _('Answers for tickets')


class QuestionnaireManager(models.Manager):
    def active(self, event):
        return self.get_queryset().filter(event=event, deadline__gte=timezone.now())


class QuestionnaireForEvent(KonferaModel, models.Model):
    questionnaire = models.OneToOneField('dynamic_forms.FormModel', on_delete=models.CASCADE)
    event = models.ForeignKey('konfera.Event', on_delete=models.CASCADE)
    deadline = models.DateTimeField()

    def __str__(self):
        return _('Questionnaire {name} for {event}').format(name=self.questionnaire.name, event=self.event.title)

    objects = QuestionnaireManager()
