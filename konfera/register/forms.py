from django import forms

from konfera.models import Ticket


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'first_name', 'last_name', 'email', 'phone', 'description')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs\
            .update({
                'required': 'required',
                'placeholder': 'Please tell us something about yourself...'
            })
