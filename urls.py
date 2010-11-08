from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
import os.path
import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # XXX TODO : Move those URLs inside the TN product

    # The wall page for generic accounts
    (r'^$',                                     'twistranet.views.home'),
    
    # Account pages
    (r'^account/(\d+)/$',                       'twistranet.views.account_by_id'),              # The 'profile' page
    (r'^account/(\w+)/$',                       'twistranet.views.account_by_slug'),
    
    # Resource links (w/ id or w/ alias or from an account or content)
    (r'^resource/(\d+)$',                       'twistranet.views.resource_by_id'),
    (r'^resource/new$',                         'twistranet.views.create_resource'),
    (r'^resource/(\w+)$',                       'twistranet.views.resource_by_alias_or_id'),
    (r'^account/(\d+)/resource/(\w+)$',         'twistranet.views.resource_by_account'),    # Fetch by account pty
    (r'^content/(\d+)/resource/(\w+)$',         'twistranet.views.resource_by_content'),    # Fetch by content pty
    
    # Media links. Used for media creation and edition only. Access is still made via the 'resource' links
    (r'^media_resource/new$',                   'twistranet.views.create_media'),
    (r'^media_resource/(\d+)/edit$',            'twistranet.views.edit_media'),
    (r'^media_library/(\d+)$',                  'twistranet.views.view_media_library'),
    
    # Content links
    (r'^content/(\d+)$',                        'twistranet.views.content_by_id'),
    (r'^content/new/(\w+)$',                    'twistranet.views.create_content'),
    (r'^content/(\d+)/edit$',                   'twistranet.views.edit_content'),
    (r'^content/(\d+)/delete$',                 'twistranet.views.delete_content'),

    # Community pages. Remember that a community IS an account, so the account views will be available as well for 'em
    (r'^communities/$',                         'twistranet.views.communities'),
    (r'^community/(\d+)/edit$',                 'twistranet.views.edit_community'),
    (r'^community/(\d+)/delete$',               'twistranet.views.delete_community'),
    (r'^community/new$',                        'twistranet.views.create_community'),
    (r'^community/(\d+)$',                      'twistranet.views.community_by_id'),
    (r'^community/(\w+)$',                      'twistranet.views.community_by_slug'),

    # Search engine (Haystack)
    (r'^search/',                               include('twistranet.urls.search')),

    # Login / Logout / Register stuff
    (r'^login/$', login),
    (r'^logout/$', logout),
    
    # TwistraNet's API
    (r'^api/', include('twistranet.api.urls')),

    # Static stuff
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static" % (os.path.dirname(__file__), settings.THEME_NAME)}),
    (r'^js/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static/js" % (os.path.dirname(__file__), settings.THEME_NAME)}),
    (r'^images/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static/images" % (os.path.dirname(__file__), settings.THEME_NAME)}), 
    (r'^css/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': "%s/twistranet/themes/%s/static/css" % (os.path.dirname(__file__), settings.THEME_NAME)}),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)


