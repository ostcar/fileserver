# -*- coding: utf-8 -*-

from django.conf import settings

def loged_in(request):
    return {'need_password': bool(settings.LOGIN_PASSWORD) or
                bool(settings.ADMIN_PASSWORD),
            'loged_in': request.session.get('loged_in', False)}

