from django import forms

from konfera.models import Speaker, Talk, Ticket


class SpeakerForm(forms.ModelForm):

    class Meta:
        model = Speaker
        exclude = ['sponsor']


class TalkForm(forms.ModelForm):

    class Meta:
        model = Talk
        exclude = ['status', 'primary_speaker', 'secondary_speaker', 'event']


class VolunteerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'first_name', 'last_name', 'email', 'phone', 'description')
