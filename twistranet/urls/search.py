from django.conf.urls.defaults import *
from twistranet.views.search_views import TwistraNetSearchView


urlpatterns = patterns('haystack.views',
    url(r'^$', TwistraNetSearchView(), name='haystack_search'),
)

