
from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext_lazy, ugettext as _
from django.core.files.storage import default_storage


class LoginForm(forms.Form):
    password = forms.fields.CharField(
        widget=forms.PasswordInput(attrs={'id':'appendedInputButton'}))

    def clean_password(self):
        data = self.cleaned_data['password']
        if data in [settings.LOGIN_PASSWORD, settings.ADMIN_PASSWORD]:
            return data
        else:
            raise ValidationError(_('Wrong password'))


class UploadForm(forms.Form):
    file = forms.fields.FileField()


class CreateSubdirectoryForm(forms.Form):
    name = forms.fields.CharField()


class TodoForm(forms.Form):
    todo = forms.fields.CharField(widget=forms.Textarea, required=False)
    old_hash = forms.fields.CharField(widget=forms.HiddenInput, required=False)


    def clean(self):
        if default_storage.exists('todo.txt'):
            todo = default_storage.open('todo.txt')
            old_hash = hash("".join(todo.readlines()))
            todo.close()
        else:
            old_hash = hash('')
        if old_hash != int(self.cleaned_data['old_hash']):
            raise ValidationError(_('The File has changed'))
        return self.cleaned_data


class UpdateDirectoryForm(forms.Form):
    old_name = forms.fields.CharField(widget=forms.HiddenInput)
    new_name = forms.fields.CharField(
        widget=forms.TextInput(attrs={'class':'snap-size'}))
