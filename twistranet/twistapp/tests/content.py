"""
This is a set of account permissions tests
"""
from twistranet.twistapp.tests.base import TNBaseTest
from twistranet.twistapp.models import *
from twistranet.content_types import *
from twistranet.twistapp.lib import permissions, roles
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError

from twistranet.core import bootstrap

class ContentTest(TNBaseTest):
    """
    Just to remember:
    A <=> admin
    B  => admin
    """


