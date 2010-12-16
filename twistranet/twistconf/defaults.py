# Django settings for TwistraNet project.
import os.path
import sys

TWISTRANET_PACKAGE = __import__('twistranet')

HERE = os.path.dirname(os.path.abspath(TWISTRANET_PACKAGE.__file__))

DEBUG = False
TEMPLATE_DEBUG = False

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS':      False,
}

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

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

# List of defined languages for TwistraNet.
# See http://docs.djangoproject.com/en/dev/ref/settings/ for an explanation of what this lambda does here.
gettext = lambda s: s
LANGUAGES = (
    ('de', gettext('German')),
    ('en', gettext('English')),
    ('fr', gettext('French')),
)



SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(HERE, 'data', 'media')

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
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
#    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    "twistranet.lib.context_processors.security_context",
    )


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INTERNAL_IPS = ("127.0.0.1", )

AUTH_PROFILE_MODULE = "twistranet.UserAccount"

CACHE_BACKEND = "locmem:///"

ROOT_URLCONF = 'urls'

#                                                       #
#   XXX     TWISTRANET-SPECIFIC CONFIGURATION       XXX #
#                                                       #
TWISTRANET_THEME_NAME = "redbook"

THEME_DIR =  "%s/core/themes/%s" % (HERE, TWISTRANET_THEME_NAME, )

TEMPLATE_DIRS = (
    THEME_DIR,
    "%s/core/templates" % (HERE, ),
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
HAYSTACK_SITECONF = 'twistranet.core.search_sites'
HAYSTACK_SEARCH_ENGINE = "twistranet.core.lib.haystack_simplehack"


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',

    # admin stuff
    'django.contrib.admin',
    
    # 3rd party modules
    'debug_toolbar',
    'haystack',
    'piston',
    'tinymce',
    'sorl.thumbnail',
    
    # TwistraNet core stuff
    'twistranet.core',
    
    # TwistraNet extensions
    'twistranet.twistrans',
    'twistranet.twiststorage',
    #'twistranet.helloworld',
)

# Local settings.
try:
    from local_settings import *
except ImportError:
    pass

