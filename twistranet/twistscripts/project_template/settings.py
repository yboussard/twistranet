# Django settings for TwistraNet project.
import os.path
import sys

from twistranet.twistconf.defaults  import *

# Local settings.
try:
    from local_settings import *
except ImportError:
    pass