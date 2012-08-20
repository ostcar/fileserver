# -*- coding: utf-8 -*-

def loged_in(request):
    return {'loged_in': request.session.get('loged_in', False)}

