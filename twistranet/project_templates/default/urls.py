from django.conf.urls.defaults import *
from django.conf import settings
from twistranet.twistapp.urls import handler404, handler500
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Dynamic twistranet urls
    (r"^",                                      include("twistranet.twistapp.urls")),

    # Additional inclusions for extensions, etc
    (r'^search/',                               include('twistranet.search.urls')),
    (r'^download/',                             include('twistranet.twistorage.urls')),

    # The following line should be used only if your site is not behind Apache.
    (r'^static/',                               include('twistranet.twistorage.urls')),

    # 3rd party modules
    (r'^admin/',                                include(admin.site.urls)),
    (r'^tinymce/',                              include('tinymce.urls')),
)

