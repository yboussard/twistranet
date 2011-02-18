"""
Static URLs for TN
"""
from django.conf.urls.defaults import *
from django.conf import settings

# Static files for the theme
urlpatterns = patterns('',
    url(
        r'^(?P<path>.*)$', 
        'django.views.static.serve',    
        {'document_root': "%s" % settings.TWISTRANET_STATIC_PATH },
        name = "static",
    ),
)
