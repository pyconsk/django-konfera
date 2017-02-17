from django import forms
from django.utils.translation import ugettext_lazy as _

from konfera.models import Ticket, DiscountCode, TicketType


class RegistrationForm(forms.ModelForm):
    required_css_class = 'required'
    error_css_class = 'error'

    type = forms.ModelChoiceField(queryset=TicketType.objects.all(),
                                  widget=forms.HiddenInput(attrs={'readonly': 'readonly'}))
    discount_code = forms.CharField(label='Promo Code', max_length=15, required=False)
    description = forms.CharField(required=True, label=_('Description'),
                                  widget=forms.Textarea({'placeholder': _('Please tell us your reason why are you '
                                                                          'applying for grant...')}),)

    class Meta:
        model = Ticket
        fields = ('type', 'title', 'first_name', 'last_name', 'email', 'phone', 'discount_code', 'description')

    def __init__(self, *args, **kwargs):
        description_required = kwargs.pop('description_required', False)
        super().__init__(*args, **kwargs)

        if not description_required:
            del(self.fields['description'])

    def clean_discount_code(self):
        data = self.cleaned_data['discount_code']

        if not data:
            return None

        try:
            discount = DiscountCode.objects.get(hash=data)
        except (DiscountCode.DoesNotExist, ValueError):
            raise forms.ValidationError(_('Invalid Promo Code.'))

        return discount
