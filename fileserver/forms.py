
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext_lazy, ugettext as _


class LoginForm(forms.Form):
    password = forms.fields.CharField(
        widget=forms.PasswordInput(attrs={'id':'appendedInputButton'}))

    def clean_password(self):
        data = self.cleaned_data['password']
        if data == settings.LOGIN_PASSWORD:
            return data
        else:
            raise ValidationError(_('Wrong password'))


class UploadForm(forms.Form):
    file = forms.fields.FileField()


class CreateSubdirectoryForm(forms.Form):
    name = forms.fields.CharField()


class TodoForm(forms.Form):
    todo = forms.fields.CharField(widget=forms.Textarea, required=False)


class UpdateDirectoryForm(forms.Form):
    old_name = forms.fields.CharField(widget=forms.HiddenInput)
    new_name = forms.fields.CharField(
        widget=forms.TextInput(attrs={'class':'snap-size'}))
