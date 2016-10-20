from django import forms
from django.utils.translation import ugettext_lazy as _

from konfera.models import Ticket


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'first_name', 'last_name', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        description_required = kwargs.pop('description_required', False)
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['description'] = forms.CharField(
            widget=forms.Textarea({'placeholder': _('Please tell us something about yourself...')}),
            required=description_required, label=_('Description'))
