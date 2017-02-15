from django import forms

from konfera.models import Speaker, Talk, Ticket, Receipt


class ReceiptForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Receipt
        exclude = ['order', 'amount']


class SpeakerForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Speaker
        exclude = ['sponsor']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['bio'].required = True
        self.fields['image'].required = True


class TalkForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Talk
        exclude = ['status', 'primary_speaker', 'secondary_speaker', 'event']


class CheckInTicket(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.status is not None:
            new_choices = [(Ticket.CHECKEDIN, 'Checked-in'), (Ticket.REGISTERED, 'Registered')]
            self.fields['status'].choices = new_choices
            self.fields['status'].widget.choices = new_choices

    class Meta:
        model = Ticket
        fields = ['status']
