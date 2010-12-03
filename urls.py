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
)


