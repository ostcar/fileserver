# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView, View
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper

from .utils.filesystem import Folder


frontpage = TemplateView.as_view(template_name='fileserver/frontpage.html')


class FolderView(TemplateView):
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


class DownloadView(View):
    def get(self, request, *args, **kwargs):
        requested_file = default_storage.open(kwargs['path'])
        filename = os.path.basename(kwargs['path'])
        # TODO: Get content_type and filename
        response = HttpResponse(FileWrapper(requested_file), content_type='application/text')
        response['Content-Disposition'] = 'attachment; %s' % filename
        return response

download = DownloadView.as_view()
