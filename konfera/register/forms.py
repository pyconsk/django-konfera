from django import forms
from django.utils.translation import ugettext_lazy as _

from konfera.models import Ticket, DiscountCode


class RegistrationForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    class Meta:
        model = Ticket
        fields = ('title', 'first_name', 'last_name', 'email', 'phone', 'discount_code')

    def __init__(self, *args, **kwargs):
        description_required = kwargs.pop('description_required', False)
        super().__init__(*args, **kwargs)

        self.fields['discount_code'] = forms.CharField(label='Promo Code', max_length=15, required=False)

        if description_required:
            self.fields['description'] = forms.CharField(
                widget=forms.Textarea({'placeholder': _('Please tell us something about yourself...')}),
                required=True, label=_('Description'))

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'col-sm-10 form-control'

    def clean_discount_code(self):
        data = self.cleaned_data['discount_code']

        if data:
            try:
                discount = DiscountCode.objects.get(hash=data)
            except (DiscountCode.DoesNotExist, ValueError):
                raise forms.ValidationError(_('Invalid Promo Code.'))

            return discount

        return None
