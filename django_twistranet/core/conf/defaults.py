# Django settings for TwistraNet project.
import os.path
import sys
import logging

# Twistranet default settings.

# XXXXXXXXXXXX
# The following section is the most likely to be changed.
# XXXXXXXXXXXX

# Twistranet Theme.
TWISTRANET_THEME_NAME = "redbook"

# Default twistranet sending email
SERVER_EMAIL = "twistranet <twistranet@numericube.com>"

# Number of friends or communities displayed in a box
TWISTRANET_NETWORK_IN_BOXES = 6
TWISTRANET_FRIENDS_IN_BOXES = 9
TWISTRANET_CONTENT_PER_PAGE = 25
TWISTRANET_COMMUNITIES_PER_PAGE = 25
TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS = 9

TWISTRANET_LOG_LEVEL = logging.WARNING

# XXXXXXXXXXXX
# End of the conveniently-changeable section.
# XXXXXXXXXXXX

TN_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "../..",
))
THEME_DIR =  "%s/themes/%s" % (TN_ROOT , TWISTRANET_THEME_NAME, )

TEMPLATE_DIRS = (
    THEME_DIR,
    "%s/templates" % (TN_ROOT , ),
)
TWISTRANET_DEFAULT_RESOURCES_DIR = "%s/twistranet/fixtures/resources" % (TN_ROOT , )

# Contrib.auth module settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# TinyMCE configuration
TINYMCE_JS_URL = "/static/js/tiny_mce/tiny_mce.js"
TINYMCE_JS_ROOT = "%s/static/tiny_mce" % THEME_DIR
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,emotions,paste,searchreplace",
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
}

# Search engine (Haystack) configuration
HAYSTACK_SITECONF = 'twistranet.twistranet.search_sites'
HAYSTACK_SEARCH_ENGINE = "twistranet.twistranet.lib.haystack_simplehack"
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 20
