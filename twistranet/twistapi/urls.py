from django.conf.urls.defaults import *
import statuses

# Statuses patterns
urlpatterns = patterns('',
    url(r'^statuses/show/(?P<id>[^/]+)\.(?P<emitter_format>.+)$',   statuses.show),
    url(r'^statuses/public_timeline\.(?P<emitter_format>.+)$',      statuses.public_timeline),
)

urlpatterns += patterns(
    'piston.authentication',
    url(r'^oauth/request_token/$','oauth_request_token'),
    url(r'^oauth/authorize/$','oauth_user_auth'),
    url(r'^oauth/access_token/$','oauth_access_token'),
)
