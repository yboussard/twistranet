
from django.conf.urls.defaults import *

import settings
from twistranet.core.views import *

urlpatterns = patterns('',
    # Dynamic twistranet urls
    ("^", include("twistranet.core.urls")),
    (r'^tinymce/', include('tinymce.urls')),
)
