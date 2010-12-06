# Django settings for TwistraNet project.
# Do not overload
# Use local_settings at your project root instead
import os.path
import sys

TWISTRANET_PACKAGE = __import__('twistranet')
TWISTRANET_PATH = os.path.dirname(os.path.abspath(TWISTRANET_PACKAGE.__file__))
URL_BASE_PATH = os.path.join(TWISTRANET_PATH,"core")


DEBUG = False
TEMPLATE_DEBUG = False
TEMPLATE_STRING_IF_INVALID = "BOUH"

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS':      False,
}

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'sqlite3' 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': "twistranet",            # Name or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
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
MEDIA_ROOT = ''

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
    "twistranet.core.lib.context_processors.security_context",
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

AUTH_PROFILE_MODULE = "core.UserAccount"

CACHE_BACKEND = "locmem:///"

ROOT_URLCONF = 'urls'

THEME_NAME = "redbook"
#THEME_NAME = "default"

TEMPLATE_DIRS = (
    "%s/themes/%s" % (URL_BASE_PATH, THEME_NAME, ),
    "%s/templates" % (URL_BASE_PATH, ),
)


LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# Search engine (Haystack) configuration
HAYSTACK_SITECONF = 'twistranet.core.search_sites'
HAYSTACK_SEARCH_ENGINE = "simple"

# Twistranet settings
# XXX TODO: Put this in a twistranet.settings module?
TWISTRANET_DEFAULT_RESOURCES_DIR = "%s/themes/%s/resources" % (URL_BASE_PATH, THEME_NAME)
TWISTRANET_ACCOUNT_MEDIA_PATH = "" # path where media are stored
TWISTRANET_IMPORT_SAMPLE_DATA = True            # Make this False if you don't want sample data when bootstraping

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
    
    # TwistraNet core stuff
    'twistranet.core',
    
    # TwistraNet extensions
    'twistranet.trans',
    'twistranet.core.helloworld',
)

