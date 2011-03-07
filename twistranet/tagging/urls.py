from django.conf.urls.defaults import *
from twistranet.core.views import AsView
from twistranet.twistapp.lib.slugify import SLUG_REGEX
from views import *

urlpatterns = patterns('haystack.views',                                 
    url(r'^json$',                      AsView(SearchTagsJSON),             name = SearchTagsJSON.name),
    url(r'^(\d+)/$',                    AsView(TagView, lookup = 'id'),     name = 'tag_by_id'),
    url(r'^(%s)/$' % SLUG_REGEX,        AsView(TagView, lookup = 'slug'),   name = 'tag_by_slug'),
)

