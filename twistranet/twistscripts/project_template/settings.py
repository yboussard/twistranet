# Django settings for TwistraNet project.
import os.path
import sys

HERE = os.path.abspath(os.path.dirname(__file__))


# Local settings.
try:
    from local_settings import *
except ImportError:
    pass