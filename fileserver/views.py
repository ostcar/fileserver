# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from .utils.filesystem import Folder
from .utils.views import LogedInMixin
from .forms import LoginForm


frontpage = TemplateView.as_view(template_name='fileserver/frontpage.html')


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


class FolderView(LogedInMixin, TemplateView):
    template_name = 'fileserver/folder.html'

    def get_context_data(self, **kwargs):
        context = super(FolderView, self).get_context_data(**kwargs)
        path = kwargs.pop('path')
        context['folder'] = Folder(path)
        if path:
            context['back_url'] = reverse('fileserver_folder', args=[
                os.path.join(path, '..')])
        return context


serve_folder = FolderView.as_view()


class DownloadView(LogedInMixin, View):
    def get(self, request, *args, **kwargs):
        requested_file = default_storage.open(kwargs['path'])
        filename = os.path.basename(kwargs['path'])
        # TODO: Get content_type and filename
        response = HttpResponse(FileWrapper(requested_file), content_type='application/text')
        response['Content-Disposition'] = 'attachment; %s' % filename
        return response

download = DownloadView.as_view()
