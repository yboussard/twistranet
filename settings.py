# Django settings for TwistraNet project.
import os.path
import sys

from twistconf.global_settings  import *

# Local settings.
try:
    from local_settings import *
except ImportError:
    pass  