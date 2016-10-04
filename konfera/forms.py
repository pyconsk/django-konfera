from django import forms

from konfera.models import Speaker, Talk, Ticket



class VolunteerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'first_name', 'last_name', 'email', 'phone', 'description')
