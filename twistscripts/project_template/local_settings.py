import os.path            
HERE = os.path.dirname(__file__)

# local settings for devel mode

DEBUG = True
TEMPLATE_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': "%s/data/tn.db" % (HERE, ),     # Or path to database file if using sqlite3.
        'USER': '',                             # Not used with sqlite3.
        'PASSWORD': '',                         # Not used with sqlite3.
        'HOST': '',                             # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                             # Set to empty string for default. Not used with sqlite3.
    }
}

TWISTRANET_ACCOUNT_MEDIA_PATH = "%s/data/media" % (HERE, )

SECRET_KEY = '%(SECRET_KEY)s'

# if you want to use your own theme or templates
# you can do it here 
# XXX TODO : add in script installer (when -t option is used)

"""
THEME_NAME = "mytheme"

URL_BASE_PATH = HERE   

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "%s/themes/%s" % (HERE, THEME_NAME, ),
    "%s/templates" % (HERE, ),
)

TWISTRANET_DEFAULT_RESOURCES_DIR = "%s/themes/%s/resources" % (HERE, THEME_NAME)

"""
