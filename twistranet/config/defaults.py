# Django settings for TwistraNet project.
import os.path
import sys
import logging

from django.conf import settings

# Twistranet default settings.

# XXXXXXXXXXXX
# The following section is the most likely to be changed.
# XXXXXXXXXXXX

# Some path information
TWISTRANET_MEDIA_URL = getattr(settings, "TWISTRANET_MEDIA_URL", settings.MEDIA_URL)

# Number of friends or communities displayed in a box
TWISTRANET_NETWORK_IN_BOXES = 6
TWISTRANET_FRIENDS_IN_BOXES = 9
TWISTRANET_CONTENT_PER_PAGE = 25
TWISTRANET_COMMUNITIES_PER_PAGE = 25
TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS = 9

# Live Search behaviour
LIVE_SEARCH_RESULTS_NUMBER = 7

# Log settings
TWISTRANET_LOG_LEVEL = logging.WARNING

# XXXXXXXXXXXX
# End of the conveniently-changeable section.
# XXXXXXXXXXXX

# TinyMCE configuration
TINYMCE_FILEBROWSER = False
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,emotions,paste,searchreplace,inlinepopups,advimage",
    'theme': "advanced",
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align' : "left",
    'auto_focus': True,
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'theme_advanced_blockformats': "p,div,h2,h3,h4,h5,h6,blockquote,dt,dd,code,samp",
    'width': "490px",
    'theme_advanced_buttons1': "newdocument,|,cut,copy,paste,|,removeformat,|,undo,redo,|,link,unlink,|,charmap,emotions,|,image,|,code",
    'theme_advanced_buttons2': "formatselect,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,bullist,numlist,outdent,indent",
    'theme_advanced_buttons3': "",
    'file_browser_callback' : 'twistranet.tinymceBrowser'
}

# Sorl-thumbnail config
THUMBNAIL_PREFIX = "cache/"
THUMBNAIL_FORMAT = "PNG"
THUMBNAIL_COLORSPACE = None

# Quickupload configuration
QUICKUPLOAD_AUTO_UPLOAD = True
QUICKUPLOAD_FILL_TITLES = False 
QUICKUPLOAD_SIZE_LIMIT = 0  
QUICKUPLOAD_SIM_UPLOAD_LIMIT = 1

# Search engine (Haystack) configuration
HAYSTACK_SITECONF = 'twistranet.search.search_sites'
HAYSTACK_SEARCH_ENGINE = "twistranet.search.haystack_simplehack"
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20

# Model Translation registry module name
TRANSLATION_REGISTRY = "twistranet.translation"
