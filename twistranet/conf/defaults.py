# Django settings for TwistraNet project.
import os.path
import sys

TWISTRANET_PACKAGE = __import__('twistranet')
HERE = os.path.dirname(os.path.abspath(TWISTRANET_PACKAGE.__file__))

TWISTRANET_THEME_NAME = "redbook"

THEME_DIR =  "%s/twistranet/themes/%s" % (HERE, TWISTRANET_THEME_NAME, )

TEMPLATE_DIRS = (
    THEME_DIR,
    "%s/twistranet/templates" % (HERE, ),
)
TWISTRANET_DEFAULT_RESOURCES_DIR = "%s/resources" % THEME_DIR

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

# Sorl-thumbnail config
THUMBNAIL_PREFIX = "cache/"
THUMBNAIL_FORMAT = "PNG"

# Search engine (Haystack) configuration
HAYSTACK_SITECONF = 'twistranet.twistranet.search_sites'
HAYSTACK_SEARCH_ENGINE = "twistranet.twistranet.lib.haystack_simplehack"

