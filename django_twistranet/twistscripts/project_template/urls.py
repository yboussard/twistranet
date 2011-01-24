
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Dynamic twistranet urls
    ("^", include("django_twistranet.urls")),
    (r'^tinymce/', include('tinymce.urls')),
)
