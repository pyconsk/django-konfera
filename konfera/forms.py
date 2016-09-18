from django import forms
from konfera.models import Speaker, Talk


class SpeakerForm(forms.ModelForm):
    class Meta:
        model = Speaker
        fields = '__all__'


class TalkForm(forms.ModelForm):
    class Meta:
        model = Talk
        exclude = ['status']