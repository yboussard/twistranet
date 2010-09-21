from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
import os.path

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^TwistraNet/', include('TwistraNet.foo.urls')),

    # The wall page for currently logged-in user
    (r'^$',                                     'twistranet.views.wall'),
    (r'^account/(?P<account_id>\d+)/$',         'twistranet.views.account'),

    # Login / Logout / Register stuff
    (r'^login/$', login),
    (r'^logout/$', logout),

    # Static stuff
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/templates/static" % (os.path.dirname(__file__))}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
