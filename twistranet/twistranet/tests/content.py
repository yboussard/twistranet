"""
This is a set of account permissions tests
"""
from django.test import TestCase
from twistranet.twistranet.models import *
from twistranet.twistranet.lib import permissions, roles
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError

from twistranet.twistranet.lib import dbsetup

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
        dbsetup.bootstrap()
        dbsetup.repair()
        __account__ = SystemAccount.get()
        self.system = __account__
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.admin = UserAccount.objects.get(user__username = "admin").account_ptr

