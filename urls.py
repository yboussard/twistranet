from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
import os.path
import settings
from twistranet.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Dynamic twistranet urls
    ("^", include("twistranet.urls")),
    
    # Static stuff  depending on settings
    # TODO in future : a ttw control panel for settings
        
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/themes/%s/static" % (settings.URL_BASE_PATH, settings.THEME_NAME)}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/themes/%s/static/js" % (settings.URL_BASE_PATH, settings.THEME_NAME)}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/themes/%s/static/images" % (settings.URL_BASE_PATH, settings.THEME_NAME)}), 
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/themes/%s/static/css" % (settings.URL_BASE_PATH, settings.THEME_NAME)}),    
)


