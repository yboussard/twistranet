from django.conf.urls.defaults import *
from twistranet.core.views import AsView
from views import TwistraNetSearchView, TwistraNetJSONSearchView 


urlpatterns = patterns('haystack.views',                                 
    url(r'^json$', AsView(TwistraNetJSONSearchView), name='haystack_live_search'),
    url(r'^$', AsView(TwistraNetSearchView), name='haystack_search'),    
)

