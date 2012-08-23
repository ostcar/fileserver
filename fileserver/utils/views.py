# -*- coding: utf-8 -*-
import os
import urlparse
import urllib

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict
from django.views.defaults import permission_denied


class LogedInMixin(object):
    need_login = True
    require_admin = False

    def dispatch(self, request, *args, **kwargs):
        if (not settings.LOGIN_PASSWORD or
                request.session.get('loged_in', False) or
                not self.need_login):
            self.is_admin = False
            if not settings.ADMIN_PASSWORD or request.session.get('is_admin', False):
                self.is_admin = True
            elif self.require_admin:
                return permission_denied(request)
            request.session.modified = True
            return super(LogedInMixin, self).dispatch(request, *args, **kwargs)
        else:
            next = request.get_full_path()
            login_url = reverse('fileserver_login')
            login_url_parts = list(urlparse.urlparse(login_url))
            if next:
                querystring = QueryDict(login_url_parts[4], mutable=True)
                querystring['next'] = next
                login_url_parts[4] = querystring.urlencode(safe='/')
            return HttpResponseRedirect(urlparse.urlunparse(login_url_parts))

    def get_context_data(self, **kwargs):
        context = super(LogedInMixin, self).get_context_data(**kwargs)
        context['is_admin'] = self.is_admin
        return context


class SetPathMixin(object):
    def get_path(self):
        return urllib.unquote(self.kwargs.get('path', ''))

    def get_context_data(self, **kwargs):
        context = super(SetPathMixin, self).get_context_data(**kwargs)
        path = self.get_path()
        context['path'] = [('', 'index')]
        for directory in path.split(os.sep):
            if not directory or directory == '.':
                continue
            name = os.path.basename(directory)
            context['path'].append((directory, name))
        context['full_path'] = path
        return context
