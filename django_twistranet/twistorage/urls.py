"""
Static URLs for TN
"""
from django.conf.urls.defaults import *
from django.conf import settings

# Static files for the theme
urlpatterns = patterns('',
    (r'^/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s" % settings.TWISTRANET_STATIC_PATH }),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/js" % settings.TWISTRANET_STATIC_PATH }),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/images" % settings.TWISTRANET_STATIC_PATH}), 
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/css" % settings.TWISTRANET_STATIC_PATH }),  
)
