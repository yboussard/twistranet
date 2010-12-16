"""
Static URLs for TN
"""
from django.conf.urls.defaults import *
import settings
urlpatterns = patterns('',
    # Static files for the theme
    (r'^/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/static" % settings.THEME_DIR }),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/static/js" % settings.THEME_DIR }),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/static/images" % settings.THEME_DIR}), 
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/static/css" % settings.THEME_DIR }),  
)

