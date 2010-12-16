from django.conf.urls.defaults import *
from twistranet.core.views.search_views import TwistraNetSearchView
from twistranet.core.views import *


urlpatterns = patterns('haystack.views',
    url(r'^$', AsView(TwistraNetSearchView), name='haystack_search'),
)

