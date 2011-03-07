# Django settings for TwistraNet project.
# NEVER WRITE THIS FILE DIRECTLY, but copy/paste your settings in the local_settings.py file.
import os.path
HERE = os.path.dirname(__file__)

# Tiny config
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

# debug settings
import logging
TWISTRANET_LOG_LEVEL = logging.WARNING
if os.environ.has_key("TWISTRANET_DEBUG"):
    DEBUG = True
    TEMPLATE_DEBUG = True
    TEMPLATE_STRING_IF_INVALID = "<invalid>"
    THUMBNAIL_DEBUG = True      # sorl-thumbnail debug mode
    TWISTRANET_LOG_LEVEL = logging.DEBUG
    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS':      False,
    }
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    DEBUG = False

# Use TWISTRANET_NOMAIL environ variable to completely disable email sending.
# This is useful when boostraping TN
if os.environ.has_key("TWISTRANET_NOMAIL"):
    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Defined database engines.
# You can always overload yours in your local_settings.py file.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': "%s/var/tn.db" % (HERE, ),      # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# Only 1 is supported by twistranet anyway
SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(HERE, 'www', )
TWISTRANET_MEDIA_ROOT = os.path.join(HERE, 'var', 'upload')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

# See http://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATE_CONTEXT_PROCESSORS
_TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    DEBUG and 'django.core.context_processors.debug' or None,
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
)
TEMPLATE_CONTEXT_PROCESSORS = [ a for a in _TEMPLATE_CONTEXT_PROCESSORS if a ]

_MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'twistranet.core.middleware.RuntimePathsMiddleware',
    DEBUG and 'debug_toolbar.middleware.DebugToolbarMiddleware' or None,
)
MIDDLEWARE_CLASSES = [ a for a in _MIDDLEWARE_CLASSES if a ]

INTERNAL_IPS = ("127.0.0.1", )

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_PROFILE_MODULE = "twistapp.UserAccount"

ROOT_URLCONF = 'urls'

TEST_RUNNER = 'twistranet.core.test_runner.TwistranetTestRunner'

#                                                       #
#            TWISTRANET-SPECIFIC CONFIGURATION          #
#                                                       #
# Theme app
TWISTRANET_THEME_APP = "twistranet.themes.twistheme"
TWISTRANET_STATIC_PATH = os.path.join(HERE, 'www', 'static')

# Some project-dependant settings
TINYMCE_JS_URL = "/static/js/tiny_mce/tiny_mce.js"
TINYMCE_JS_ROOT = "%s/static/tiny_mce" % HERE

# Cache tuning
CACHE_BACKEND = "locmem:///"
TWISTRANET_CACHE_USER = 60*5            # User-centric data stored for xx second

# Twistranet default settings.

# XXXXXXXXXXXX
# The following section is the most likely to be changed.
# XXXXXXXXXXXX

# Number of friends or communities displayed in a box
TWISTRANET_NETWORK_IN_BOXES = 6
TWISTRANET_FRIENDS_IN_BOXES = 9
TWISTRANET_CONTENT_PER_PAGE = 25
TWISTRANET_COMMUNITIES_PER_PAGE = 25
TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS = 9

# Live Search behaviour
LIVE_SEARCH_RESULTS_NUMBER = 7

# The following lines are for default admin user created at bootstrap
TWISTRANET_DEFAULT_ADMIN_USERNAME = "admin"
TWISTRANET_DEFAULT_ADMIN_FIRSTNAME = "Administrator"
TWISTRANET_DEFAULT_ADMIN_LASTNAME = ""

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


# Basic apps installation. You may add your own modules here.
_INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',

    # admin stuff
    'django.contrib.admin',
    
    # 3rd party modules
    DEBUG and 'debug_toolbar' or None,
    'piston',
    'tinymce',
    'sorl.thumbnail',
    'modeltranslation',
    
    # TwistraNet core stuff
    'twistranet.twistapp',
    'twistranet.search',
    
    # Twistranet theme
    TWISTRANET_THEME_APP,
    
    # TwistraNet extensions
    'twistranet.content_types',
    'twistranet.notifier',
    'twistranet.twistorage',
    'twistranet.tagging',

    # 3rd party modules - must be loaded AFTER TN
    'haystack',
)
INSTALLED_APPS = [a for a in _INSTALLED_APPS if a]

# Contrib.auth module settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Settings that should get altered with BASE_URL configuration.
# This is used in RuntimePathsMiddleware to ensure all TN settings
# are set with the correct URL.
BASE_URL_DEPDENDANT = (
    "MEDIA_URL",
    "ADMIN_MEDIA_PREFIX",
    "LOGIN_URL",
    "LOGOUT_URL",
    "LOGIN_REDIRECT_URL",
    "TINYMCE_JS_URL",
)

# Local and bootstrap settings.
TWISTRANET_IMPORT_SAMPLE_DATA = False
TWISTRANET_IMPORT_COGIP = False
try:
    from bootstrap_settings import *
except ImportError:
    pass
try:
    from local_settings import *
except ImportError:
    pass
