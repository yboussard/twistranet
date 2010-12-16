import os.path            
HERE = os.path.dirname(__file__)

# local settings

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
TWISTRANET_IMPORT_SAMPLE_DATA = True            # Make this False if you don't want sample data when bootstraping

SECRET_KEY = '%(SECRET_KEY)s'



""" ### START -t OPTION

THEME_NAME = "redbook"

URL_BASE_PATH = HERE   

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "%s/themes/%s" % (HERE, THEME_NAME, ),
    "%s/templates" % (HERE, ),
)

TWISTRANET_DEFAULT_RESOURCES_DIR = "%s/themes/%s/resources" % (HERE, THEME_NAME)

 ### END -t OPTION """
