from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
import os.path
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^TwistraNet/', include('TwistraNet.foo.urls')),

    # The wall page for currently logged-in user
    (r'^$',                                     'twistranet.views.home'),
    (r'^account/(\d+)/$',                       'twistranet.views.account_by_id'),
    
    # Resource links (w/ id or w/ alias or from an account or content)
    (r'^resource/(\d+)$',                       'twistranet.views.resource_by_id'),
    (r'^resource/(\w+)$',                       'twistranet.views.resource_by_alias_or_id'),
    (r'^account/(\d+)/resource/(\w+)$',         'twistranet.views.resource_by_account'),    # Fetch by account pty
    (r'^content/(\d+)/resource/(\w+)$',         'twistranet.views.resource_by_content'),    # Fetch by content pty

    # Login / Logout / Register stuff
    (r'^login/$', login),
    (r'^logout/$', logout),

    # Static stuff
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static" % (os.path.dirname(__file__), settings.THEME_NAME)}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static/js" % (os.path.dirname(__file__), settings.THEME_NAME)}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static/images" % (os.path.dirname(__file__), settings.THEME_NAME)}),
    # (r'^static/(?P<path>.*)$', 'django.views.static.serve',
    #         {'document_root': "%s/twistranet/templates/static" % (os.path.dirname(__file__))}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
