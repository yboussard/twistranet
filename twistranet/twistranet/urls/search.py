from django.conf.urls.defaults import *
from twistranet.twistranet.views.search_views import TwistraNetSearchView
from twistranet.twistranet.views import *


urlpatterns = patterns('haystack.views',
    url(r'^$', AsView(TwistraNetSearchView), name='haystack_search'),
)

