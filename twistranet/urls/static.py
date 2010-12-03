"""
Static URLs for TN
"""
from django.conf.urls.defaults import *
import settings
print settings.HERE
urlpatterns = patterns('',
    (r'^/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static" % (settings.HERE, settings.TWISTRANET_THEME_NAME)}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static/js" % (settings.HERE, settings.TWISTRANET_THEME_NAME)}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static/images" % (settings.HERE, settings.TWISTRANET_THEME_NAME)}), 
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static/css" % (settings.HERE, settings.TWISTRANET_THEME_NAME)}),    
)

