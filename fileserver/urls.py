from django.conf.urls import patterns, include, url

urlpatterns = patterns('fileserver.views',
    url(r'^$', 'frontpage', name='fileserver_frontpage'),
    url(r'^login$', 'login', name='fileserver_login'),
    url(r'^index/(?P<path>.*)', 'serve_folder', name='fileserver_folder'),
    url(r'^download/(?P<path>.*)', 'download', name='fileserver_download'),
)
