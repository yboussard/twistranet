from django.conf.urls.defaults import *
import os.path
from twistranet.twistranet.views import *
from twistranet.twistranet.lib.slugify import SLUG_REGEX

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # The wall page for generic accounts
    url(r'^$',                                      AsView(HomepageView), name = HomepageView.name),
    url(r'^timeline$',                              AsView(PublicTimelineView), name = PublicTimelineView.name),
    
    # Account pages 
    url(r'^account/(\d+)/$',                        AsView(UserAccountView, lookup = 'id'), name = 'account_by_id'),              # The 'profile' page
    url(r'^account/(%s)/$' % SLUG_REGEX,            AsView(UserAccountView, lookup = 'slug'), name = 'account_by_slug'),
    url(r'^account/(\d+)/communities/$',            AsView(AccountCommunitiesView), name='account_communities'),
    url(r'^account/(\d+)/network/$',                AsView(AccountNetworkView), name='account_network'),
    url(r'^account/(\d+)/edit$',                    AsView(UserAccountEdit), name = "user_account_edit"),              
    url(r'^account/new$',                           AsView(UserAccountCreate), name = "user_account_create", ),
    url(r'^account/(\d+)/add_to_network/$',         AsView(AddToNetworkView), name = AddToNetworkView.name),
    url(r'^account/(\d+)/remove_from_network/$',    AsView(RemoveFromNetworkView), name = RemoveFromNetworkView.name),
    url(r'^pending_network/$',                      AsView(PendingNetworkView), name = PendingNetworkView.name),
    
    # Resource links (w/ id or w/ alias or from an account or content)
    url(r'^resource/(\d+)$',                    'twistranet.twistranet.views.resource_by_id', name='resource_by_id'),
    url(r'^resource/(%s)/$' % SLUG_REGEX,       'twistranet.twistranet.views.resource_by_slug', name='resource_by_slug'),
    (r'^resource/new$',                         'twistranet.twistranet.views.create_resource'),      
    (r'^resource/(\w+)$',                       'twistranet.twistranet.views.resource_by_slug_or_id'),  
    (r'^resource_by_publisher/json/(\d+)$',     'twistranet.twistranet.views.resource_by_publisher_json'),     # return json list of resources by publisher id
    (r'^account/(\d+)/resource/(\w+)$',         'twistranet.twistranet.views.resource_by_account'),    # Fetch by account pty
    (r'^content/(\d+)/resource/(\w+)$',         'twistranet.twistranet.views.resource_by_content'),    # Fetch by content pty   
    (r'^resource_browser/$',                    'twistranet.twistranet.views.resource_browser'),       # resource browser used by wysiwyg editors
    (r'^resource_quickupload/$',                'twistranet.twistranet.views.resource_quickupload'),   # resource quickupload ajax template
    (r'^resource_quickupload_file/$',           'twistranet.twistranet.views.resource_quickupload_file'),   # resource quickupload json response
    
    # Thumbnail cache links
    url(r'\Wcache/([\w\./]+)$',                 'twistranet.twistranet.views.resource_cache'),         # Fetch a thumb cache by its key
    url(r'^cache/([\w\./]+)$',                  'twistranet.twistranet.views.resource_cache'),         # Fetch a thumb cache by its key

    # Media links. Used for media creation and edition only. Access is still made via the 'resource' links
    url(r'^media_resource/new$',                'twistranet.twistranet.views.create_media', name = "media_create", ),
    url(r'^media_resource/(\d+)/edit$',         'twistranet.twistranet.views.edit_media', name = "media_edit", ),    
    url(r'^media_library/(\d+)$',               'twistranet.twistranet.views.view_media_library', name = "media_library_view", ),
    
    # Content links
    url(r'^content/(\d+)/$',                    AsView(ContentView, lookup = 'id'), name = 'content_by_id'),
    url(r'^content/(%s)/$' % SLUG_REGEX,        AsView(ContentView, lookup = 'slug'), name = 'content_by_slug'),
    url(r'^content/(\d+)/new/(\w+)$',           AsView(ContentCreate), name = ContentCreate.name, ),
    url(r'^content/(\d+)/edit$',                AsView(ContentEdit), name = ContentEdit.name, ),
    url(r'^content/(\d+)/delete$',              AsView(ContentDelete), name = ContentDelete.name, ),

    # Community pages. Remember that a community IS an account, so the account views will be available as well for 'em
    url(r'^community/(\d+)$',                   AsView(CommunityView, lookup = "id"), name = 'community_by_id'),
    url(r'^community/(%s)/$' % SLUG_REGEX,      AsView(CommunityView, lookup = "slug"), name = 'community_by_slug'),       
    url(r'^community/(\d+)/members$',           AsView(CommunityMembers), name = CommunityMembers.name),   
    url(r'^community/(\d+)/managers$',          AsView(CommunityManagers), name = 'community_managers'),
    url(r'^communities/$',                      AsView(CommunityListingView), name = CommunityListingView.name, ),
    url(r'^communities/my$',                    AsView(MyCommunitiesView), name = MyCommunitiesView.name, ),
    url(r'^community/(\d+)/edit$',              AsView(CommunityEdit), name = "community_edit"),
    url(r'^community/(\d+)/join$',              AsView(CommunityJoin), name = CommunityJoin.name),
    url(r'^community/(\d+)/leave$',             AsView(CommunityLeave), name = CommunityLeave.name),
    url(r'^community/(\d+)/invite$',            AsView(CommunityInvite), name = CommunityInvite.name),
    url(r'^community/(\d+)/manage_members$',    AsView(CommunityManageMembers), name = CommunityManageMembers.name),
    url(r'^community/invitations$',             AsView(CommunityInvitations), name = CommunityInvitations.name, ),
    url(r'^community/new$',                     AsView(CommunityCreate), name = CommunityCreate.name, ),
    url(r'^community/(\d+)/delete$',            AsView(CommunityDelete), name = CommunityDelete.name, ),

    # Additional inclusions for extensions, etc
    (r'^search/',                               include('twistranet.twistranet.urls.search')),
    (r'^static/',                               include('twistranet.twistranet.urls.static')),
    (r'^download/',                             include('twistranet.twistorage.urls')),

    # Login / Logout / Register stuff
    url(r'^login/$',                            AsPublicView(AccountLogin), name = AccountLogin.name),
    url(r'^logout/$',                           AsPublicView(AccountLogout), name = AccountLogout.name, ),  
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Administration pages.
    url(r'^configuration/$',                   AsView(ConfigurationEdit), name = ConfigurationEdit.name),
    (r'^admin/', include(admin.site.urls)),
)


