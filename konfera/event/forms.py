from django import forms

from konfera.models import Speaker, Talk, Receipt


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
