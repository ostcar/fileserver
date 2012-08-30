# -*- coding: utf-8 -*-
import os
from StringIO import StringIO
from wsgiref.util import FileWrapper

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateView, View, RedirectView
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.core.exceptions import SuspiciousOperation
from django.contrib import messages
from django.views.defaults import page_not_found

from extra_views import FormSetView

from .utils.filesystem import Directory, guess_type
from .utils.views import LogedInMixin, SetPathMixin
from .forms import (LoginForm, UploadForm, CreateSubdirectoryForm, TodoForm,
    UpdateDirectoryForm)


class FrontpageView(LogedInMixin, TemplateView):
    template_name = 'fileserver/frontpage.html'
    need_login = False


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
        if form.cleaned_data['password'] == settings.ADMIN_PASSWORD:
            self.request.session['is_admin'] = True

        self.request.session['loged_in'] = True
        return super(LoginView, self).form_valid(form)


login = LoginView.as_view()


class LogoutView(RedirectView):
    url = reverse_lazy('fileserver_frontpage')
    permanent = False

    def get(self, request, *args, **kwargs):
        request.session.flush()
        return super(LogoutView, self).get(request, *args, **kwargs)


logout = LogoutView.as_view()


class BrowseView(SetPathMixin, LogedInMixin, TemplateView):
    template_name = 'fileserver/browse.html'

    def get_context_data(self, **kwargs):
        context = super(BrowseView, self).get_context_data(**kwargs)
        path = self.get_path()
        sort = self.request.GET.get('sort', self.request.session.get('sort', 'name'))
        reverse = self.request.GET.get(
            'reverse', self.request.session.get('reverse', False))
        if reverse == 'false' or reverse == '0':
            reverse = False
        else:
            reverse = bool(reverse)
        self.request.session['sort'] = sort
        self.request.session['reverse'] = reverse
        context['directory'] = Directory(path, sort=sort, reverse=reverse)

        reverse = 'false' if reverse else 'true'
        context['name_url'] = "?sort=name"
        context['size_url'] = "?sort=size"
        key = {'name': 'name_url', 'size': 'size_url'}[sort]
        context[key] += "&reverse=%s" % reverse
        return context


browse = BrowseView.as_view()


class CreateSubdirectoryView(SetPathMixin, LogedInMixin, FormView):
    template_name = 'fileserver/create_subdirectory.html'
    form_class = CreateSubdirectoryForm

    def form_valid(self, form):
        new_dir = form.cleaned_data['name']
        try:
            default_storage.mkdir(os.path.join(self.get_path(), new_dir))
        except (SuspiciousOperation, OSError) as e:
            messages.error(self.request, _('Error in "%(newdir)s": %(error)s')
                                         % {'newdir': new_dir, 'error': e})
        return super(CreateSubdirectoryView, self).form_valid(form)

    def get_success_url(self):
        return reverse('fileserver_browse', args=[self.get_path()])


mkdir = CreateSubdirectoryView.as_view()


class DownloadView(SetPathMixin, LogedInMixin, View):
    def get(self, request, *args, **kwargs):
        path = self.get_path()
        try:
            requested_file = default_storage.open(path)
        except IOError:
            return page_not_found(request)
        response = HttpResponse(FileWrapper(requested_file),
                                content_type=guess_type(path))
        response['Content-Disposition'] = 'attachment'
        response['Content-Length'] = default_storage.size(path)
        return response


download = DownloadView.as_view()


class ZipDirectoryView(SetPathMixin, LogedInMixin, View):
    def get(self, request, *args, **kwargs):
        path = self.get_path()
        filename = path.split(os.sep)[-1] or 'index'
        # TODO: Find a way to use umlauts in the filename
        ascii_filename = filename.encode('ascii', 'ignore') or 'directory'
        filename = "%s.zip" % ascii_filename
        archiv = StringIO()
        default_storage.zipdir(path, archiv, include_hidden=False)
        archiv.seek(0)
        archiv.seek(0, os.SEEK_END)
        file_size = archiv.tell()
        archiv.seek(0)
        response = HttpResponse(FileWrapper(archiv),
                                content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        response['Content-Length'] = file_size
        return response


zip_directory = ZipDirectoryView.as_view()


class UploadView(SetPathMixin, LogedInMixin, FormSetView):
    form_class = UploadForm
    template_name = 'fileserver/upload.html'
    extra = 3

    def get(self, request, *args, **kwargs):
        messages.warning(self.request, _('Do not reload this page!'))
        return super(UploadView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('fileserver_browse', args=[self.get_path()])

    def formset_valid(self, formset):
        path = self.get_path()
        for form in formset:
            if 'file' in form.cleaned_data:
                file_name = os.path.join(path, form.cleaned_data['file'].name)
                default_storage.save(file_name, form.cleaned_data['file'])
        return super(UploadView, self).formset_valid(formset)


upload = UploadView.as_view()


class UpdateDirectoryView(SetPathMixin, LogedInMixin, FormSetView):
    form_class = UpdateDirectoryForm
    template_name = 'fileserver/update_directory.html'
    can_delete = True
    extra = 0
    require_admin = True

    def get_initial(self):
        directory = Directory(self.get_path())
        initial = []
        for name, url, item_count in directory.iter_subdirectories():
            initial.append(
                {'old_name': name, 'new_name': name, 'is_directory': True})

        for name, url, size in directory.iter_files():
            initial.append(
                {'old_name': name, 'new_name': name, 'is_directory': False})
        return initial

    def get(self, request, *args, **kwargs):
        messages.warning(self.request, _('You can not undo the deletion'))
        return super(UpdateDirectoryView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('fileserver_browse', args=[self.get_path()])

    def formset_valid(self, formset):
        path = self.get_path()
        for form in formset:
            old_path = os.path.join(path, form.cleaned_data['old_name'])
            if form.cleaned_data['DELETE']:
                default_storage.delete(old_path)
            else:
                new_path = os.path.join(path, form.cleaned_data['new_name'])
                if old_path != new_path:
                    try:
                        default_storage.mv(old_path, new_path)
                    except (SuspiciousOperation, OSError) as e:
                        messages.error(self.request,
                                       _('Error in "%(path)s": %(error)s')
                                       % {'path': old_path, 'error': e})

        return super(UpdateDirectoryView, self).formset_valid(formset)


edit_directory = UpdateDirectoryView.as_view()


class TodoView(LogedInMixin, FormView):
    form_class = TodoForm
    success_url = reverse_lazy('fileserver_todo')
    template_name = 'fileserver/todo.html'

    def form_valid(self, form):
        todo = default_storage.open('todo.txt', 'w')
        todo.write(form.cleaned_data['todo'].encode('utf-8'))
        todo.close()
        return super(TodoView, self).form_valid(form)

    def get_initial(self):
        if default_storage.exists('todo.txt'):
            todo = default_storage.open('todo.txt')
            content = "".join(todo.readlines())
            todo.close()
            return {'todo': content, 'old_hash': hash(content)}
        else:
            return {'todo': '', 'old_hash': hash('')}


todo = TodoView.as_view()

