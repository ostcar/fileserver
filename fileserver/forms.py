
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext_lazy, ugettext as _

class LoginForm(forms.Form):
    password = forms.fields.CharField(widget=forms.PasswordInput)

    def clean_password(self):
        data = self.cleaned_data['password']
        if data == settings.LOGIN_PASSWORD:
            return data
        else:
            raise ValidationError(_('Wrong password'))
