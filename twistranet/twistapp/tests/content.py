"""
This is a set of account permissions tests
"""
from django.test import TestCase
from twistranet.twistapp.models import *
from twistranet.content_types import *
from twistranet.twistapp.lib import permissions, roles
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError

from twistranet.core import bootstrap

class ContentTest(TestCase):
    """
    Just to remember:
    A <=> admin
    B  => admin
    """
    def setUp(self, ):
        """
        Get A and B users
        """
        bootstrap.bootstrap()
        bootstrap.repair()
        __account__ = SystemAccount.get()
        self.system = __account__
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.admin = UserAccount.objects.get(user__username = "admin").account_ptr

