import os.path            
HERE = os.path.dirname(__file__)

# local settings

DEBUG = True
TEMPLATE_DEBUG = True
TEMPLATE_STRING_IF_INVALID = "BOUH"

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

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*pzu469z6h)3mpkff#x&cdcj)6*918f6nfp7f@x2@049p2ydhz'
