"""
This is a basic wall test.
"""
from django.test import TestCase
from twistranet.twistranet.models import *
from twistranet.twistranet.lib import permissions, roles
from twistranet.twistrans.models import *
from django.core.exceptions import ValidationError, PermissionDenied

from twistranet.twistranet.lib import dbsetup

class TwistransTest(TestCase):
    """
    Just to remember:
    A <=> admin
    B  => admin
    """
    
    def setUp(self):
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
        
    def test_fixture(self,):
        """
        Test if translation fixture is loaded correctly
        """
        # Check if content has translation(s)
        __account__ = self.system
        
