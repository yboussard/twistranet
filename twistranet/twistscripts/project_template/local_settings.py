import os.path            
HERE = os.path.dirname(__file__)

# local settings

DEBUG = False
TEMPLATE_DEBUG = False

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

TWISTRANET_THEME_NAME = "redbook"

THEME_DIR =  "%s/themes/%s" % (HERE, TWISTRANET_THEME_NAME, )

TEMPLATE_DIRS = (
    THEME_DIR,
    "%s/templates" % (HERE, ),
)

TINYMCE_JS_ROOT = "%s/static/tiny_mce" % THEME_DIR

 ### END -t OPTION """
