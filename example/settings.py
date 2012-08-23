import os
from fileserver.settings import *

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

SECRET_KEY = 'REPLACE_ME_ON_DEPLOYMENT'
DEBUG = True
LOGIN_PASSWORD = ''
ADMIN_PASSWORD = ''
MEDIA_ROOT = os.path.join(SITE_ROOT, 'content')
ROOT_URLCONF = 'example.urls'
WSGI_APPLICATION = 'example.wsgi.application'
