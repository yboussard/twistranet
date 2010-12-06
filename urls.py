
from django.conf.urls.defaults import *

import settings
from twistranet.views import *

urlpatterns = patterns('',
    # Dynamic twistranet urls
    ("^", include("twistranet.urls")),
)

