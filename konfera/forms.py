from django import forms
from django.utils.translation import ugettext_lazy as _


class OrderedTicketsInlineFormSet(forms.models.BaseInlineFormSet):
    def clean(self):
        valid_forms = [form for form in self.forms if form.is_valid() and form not in self.deleted_forms]
        if valid_forms:
            event_id = valid_forms[0].cleaned_data['type'].event_id
            for form in valid_forms[1:]:
                if form.cleaned_data and form.cleaned_data['type'].event_id != event_id:
                    raise forms.ValidationError(_('All tickets must be for the same event.'))
        super().clean()
