from django.conf.urls.defaults import *
from twistranet.views.search_views import TwistraNetSearchView
from twistranet.views import *


urlpatterns = patterns('haystack.views',
    url(r'^$', AsView(TwistraNetSearchView), name='haystack_search'),
)

