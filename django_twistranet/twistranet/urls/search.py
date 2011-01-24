from django.conf.urls.defaults import *
from django_twistranet.views.search_views import TwistraNetSearchView, TwistraNetJSONSearchView 
from django_twistranet.views import *


urlpatterns = patterns('haystack.views',                                 
    url(r'^json$', AsView(TwistraNetJSONSearchView), name='haystack_live_search'),
    url(r'^$', AsView(TwistraNetSearchView), name='haystack_search'),    
)

