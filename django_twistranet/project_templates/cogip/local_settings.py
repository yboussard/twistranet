"""
Edit this file instead of editing settings.py.

settings.py is a generated file and its content can change!
"""
import os.path
import os
import logging
HERE = os.path.dirname(__file__)

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.NOTICE)

# local settings
if os.environ.has_key("TWISTRANET_DEBUG"):
    DEBUG = True
    TEMPLATE_DEBUG = True
    TEMPLATE_STRING_IF_INVALID = "BOUH"
    TWISTRANET_LOG_LEVEL = logging.DEBUG

# Default data loading
TWISTRANET_IMPORT_SAMPLE_DATA = False           # Make this False if you don't want sample data when bootstraping
TWISTRANET_IMPORT_COGIP = True                  # Make this False if you don't want sample data when bootstraping

# Make this unique, and don't share it with anybody.
SECRET_KEY = '*pzu469z6h)3mpkff#x&cdcj)6*918f6nfp7f@x2@049p2ydhz'
