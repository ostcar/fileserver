# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView, View, RedirectView
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from extra_views import FormSetView

from .utils.filesystem import Directory, save_file, guess_type
from .utils.views import LogedInMixin, SetPathMixin
from .forms import LoginForm, UploadForm, CreateSubdirectoryForm, TodoForm


class FrontpageView(SetPathMixin, TemplateView):
    template_name = 'fileserver/frontpage.html'


frontpage = FrontpageView.as_view()


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'fileserver/login.html'

    def get_success_url(self):
        redirect_to = self.request.REQUEST.get('next', '')
        if not redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL
        return redirect_to

    def form_valid(self, form):
        self.request.session['loged_in'] = True
        return super(LoginView, self).form_valid(form)


login = LoginView.as_view()


class LogoutView(RedirectView):
    url = reverse_lazy('fileserver_frontpage')

    def get(self, request, *args, **kwargs):
        request.session.flush()
        return super(LogoutView, self).get(request, *args, **kwargs)


logout = LogoutView.as_view()


class DirectoryView(SetPathMixin, LogedInMixin, TemplateView):
    template_name = 'fileserver/directory.html'

    def get_context_data(self, **kwargs):
        context = super(DirectoryView, self).get_context_data(**kwargs)
        path = kwargs.pop('path')
        context['directory'] = Directory(path)
        if path:
            context['back_url'] = reverse('fileserver_directory', args=[
                os.path.join(path, '..')])
        return context


serve_directory = DirectoryView.as_view()


class CreateSubdirectoryView(SetPathMixin, LogedInMixin, FormView):
    template_name = 'fileserver/create_subdirectory.html'
    form_class = CreateSubdirectoryForm

    def form_valid(self, form):
        new_dir = form.cleaned_data['name']
        default_storage.mkdir(os.path.join(self.get_path(), new_dir))
        return super(CreateSubdirectoryView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fileserver_directory', args=[self.get_path()])


mkdir = CreateSubdirectoryView.as_view()


class DownloadView(SetPathMixin, LogedInMixin, View):
    def get(self, request, *args, **kwargs):
        path = self.get_path()
        requested_file = default_storage.open(path)
        # TODO: Get content_type and filename
        response = HttpResponse(FileWrapper(requested_file),
                                content_type=guess_type(path))
        return response


download = DownloadView.as_view()


class UploadView(SetPathMixin, LogedInMixin, FormSetView):
    form_class = UploadForm
    template_name = 'fileserver/upload.html'

    def get_success_url(self):
        return reverse('fileserver_directory', args=[self.kwargs['path']])

    def formset_valid(self, formset):
        for form in formset:
            if 'file' in form.cleaned_data:
                save_file(self.kwargs['path'], form.cleaned_data['file'])
        return super(UploadView, self).formset_valid(formset)


upload = UploadView.as_view()


class TodoView(LogedInMixin, FormView):
    form_class = TodoForm
    success_url = reverse_lazy('fileserver_todo')
    template_name = 'fileserver/todo.html'

    def form_valid(self, form):
        todo = default_storage.open('todo.txt', 'w')
        todo.write(form.cleaned_data['todo'])
        todo.close()
        return super(TodoView, self).form_valid(form)

    def get_initial(self):
        if default_storage.exists('todo.txt'):
            todo = default_storage.open('todo.txt')
            return {'todo': "".join(todo.readlines())}
        else:
            return {}


todo = TodoView.as_view()
