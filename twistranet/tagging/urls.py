from django.conf.urls.defaults import *
from twistranet.core.views import AsView
from views import SearchTagsJSON

urlpatterns = patterns('haystack.views',                                 
    url(r'^json$',          AsView(SearchTagsJSON),       name = SearchTagsJSON.name),
)

