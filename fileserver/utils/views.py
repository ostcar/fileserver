# -*- coding: utf-8 -*-
import os
import urlparse
import urllib

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, QueryDict


class LogedInMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not settings.LOGIN_PASSWORD or request.session.get('loged_in', False):
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


class SetPathMixin(object):
    def get_path(self):
        return os.path.normpath(urllib.unquote(self.kwargs.get('path', '')))

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
