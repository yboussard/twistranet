
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Dynamic twistranet urls
    ("^", include("twistranet.twistranet.urls")),
    (r'^tinymce/', include('tinymce.urls')),
)
