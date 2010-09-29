"""
This is a set of account permissions tests
"""
from django.test import TestCase
from twistranet.models import *
from twistranet.lib import permissions

from twistranet.models import _permissionmapping, dbsetup

class AccountSecurityTest(TestCase):
    """
    Just to remember:
    A <=> PJ
    B  => PJ
    """
    
    def setUp(self):
        """
        Get A and B users
        """
        dbsetup.bootstrap()
        __account__ = SystemAccount.getSystemAccount()
        self.system = __account__
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.PJ = UserAccount.objects.get(user__username = "pjgrizel").account_ptr
    
    def test_can_see_myself(self):
        """
        Check if I can see myself
        """
        __account__ = self.A
        self.failUnless(self.A in Account.objects.all()) 
        __account__ = self.B
        self.failUnless(self.B in Account.objects.all()) 
        __account__ = self.PJ
        self.failUnless(self.PJ in Account.objects.all()) 
        
        