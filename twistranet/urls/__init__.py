from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
import os.path
from twistranet.views import *
from twistranet.lib.slugify import SLUG_REGEX

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # The wall page for generic accounts
    url(r'^$',                 AsView(HomepageView), name='twistranet_home'),
    
    # Account pages
    url(r'^account/(\d+)/communities/$', AsView(AccountCommunitiesView), name='account_communities'), 
    url(r'^account/(\d+)/network/$', AsView(AccountNetworkView), name='account_network'), 
    url(r'^account/(\d+)/$', AsView(UserAccountView, lookup = 'id'), name='account_by_id'),              # The 'profile' page
    url(r'^account/(%s)/$' % SLUG_REGEX, AsView(UserAccountView, lookup = 'slug'), name='account_by_slug'), 
    url(r'^account/(\d+)/add_to_network/$', AsView(AddToNetworkView), name = 'add_to_my_network'),
    url(r'^account/(\d+)/remove_from_network/$', AsView(RemoveFromNetworkView), name = 'remove_from_my_network'),
    url(r'^pending_network/$', AsView(PendingNetworkView), name = 'account_pending_network'),
    
    # Resource links (w/ id or w/ alias or from an account or content)
    url(r'^resource/(\d+)$', 'twistranet.views.resource_by_id', name='resource_by_id'),
    url(r'^resource/(%s)/$' % SLUG_REGEX, 'twistranet.views.resource_by_id', name='resource_by_slug'),
    (r'^resource/new$',                         'twistranet.views.create_resource'),
    (r'^resource/(\w+)$',                       'twistranet.views.resource_by_alias_or_id'),
    (r'^account/(\d+)/resource/(\w+)$',         'twistranet.views.resource_by_account'),    # Fetch by account pty
    (r'^content/(\d+)/resource/(\w+)$',         'twistranet.views.resource_by_content'),    # Fetch by content pty
    
    # Media links. Used for media creation and edition only. Access is still made via the 'resource' links
    (r'^media_resource/new$',                   'twistranet.views.create_media'),
    (r'^media_resource/(\d+)/edit$',            'twistranet.views.edit_media'),
    (r'^media_library/(\d+)$',                  'twistranet.views.view_media_library'),
    
    # Content links
    url(r'^content/(\d+)/$', 'twistranet.views.content_by_id', name='content_by_id'),
    url(r'^content/(%s)/$' % SLUG_REGEX,        'twistranet.views.content_by_slug', name='content_by_slug'),
    (r'^content/new/(\w+)$',                    'twistranet.views.create_content'),
    (r'^content/(\d+)/edit$',                   'twistranet.views.edit_content'),
    (r'^content/(\d+)/delete$',                 'twistranet.views.delete_content'),

    # Community pages. Remember that a community IS an account, so the account views will be available as well for 'em
    url(r'^community/(\d+)$', AsView(CommunityView, lookup = "id"), name='community_by_id'),
    url(r'^community/(%s)/$' % SLUG_REGEX, AsView(CommunityView, lookup = "slug"), name='community_by_slug'),
    url(r'^communities/$', AsView(CommunityListingView), name = "communities", ),
    url(r'^community/(\d+)/edit$', AsView(CommunityView, lookup = "id"), name = "community_edit"),
    url(r'^community/(\d+)/join$', 'twistranet.views.join_community', name = "community_join"),
    url(r'^community/(\d+)/leave$', 'twistranet.views.leave_community', name = "community_leave"),
    url(r'^community/new$', AsView(CommunityView), name = "community_create", ),
    (r'^community/(\d+)/delete$', 'twistranet.views.delete_community'),

    # Search engine (Haystack)
    (r'^search/',                               include('twistranet.urls.search')),
    (r'^static/',                               include('twistranet.urls.static')),

    # Login / Logout / Register stuff
    (r'^login/$', login),
    (r'^logout/$',                              'twistranet.views.account_logout'),  
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)


