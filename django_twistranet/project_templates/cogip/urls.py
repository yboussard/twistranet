from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Dynamic twistranet urls
    ("^",                                       include("django_twistranet.twistranet.urls")),

    # Additional inclusions for extensions, etc
    (r'^search/',                               include('django_twistranet.search.urls')),
    (r'^static/',                               include('django_twistranet.twistorage.urls')),
    (r'^download/',                             include('django_twistranet.twistorage.urls')),

    # 3rd party modules
    (r'^admin/',                                include(admin.site.urls)),
    (r'^tinymce/',                              include('tinymce.urls')),
)

