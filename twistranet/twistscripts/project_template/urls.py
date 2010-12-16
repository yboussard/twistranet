
from django.conf.urls.defaults import *

import settings
from twistranet.twistranet.views import *

urlpatterns = patterns('',
    # Dynamic twistranet urls
    ("^", include("twistranet.twistranet.urls")),
    (r'^tinymce/', include('tinymce.urls')),
)
