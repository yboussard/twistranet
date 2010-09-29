"""
This is a set of account permissions tests
"""
from django.test import TestCase
from twistranet.models import *
from twistranet.lib import permissions
from django.core.exceptions import ValidationError, PermissionDenied

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
        
    def test_private_account(self):
        """
        Check if I can make an account private.
        Note that private accounts are still visible in their network!
        """
        __account__ = self.A
        __account__.permissions = "private"
        __account__.save()
        self.failUnless(self.A in Account.objects.all()) 
        __account__ = self.B
        self.failIf(self.A in Account.objects.all())
        __account__ = self.PJ
        self.failUnless(self.A in Account.objects.all(), "A private account must still be listable in its network")
        
        
    def test_cant_view_attributes(self):
        """
        Fetch a restricted account and check if we can't read basic properties.
        In our example we use the 'admin' community, which is listed but can't be viewed.
        """
        # Check if we find the admin community
        __account__ = self.A
        admin = Community.objects.get(name = "Administrators")
        
        # Check community name, then the protected 'description' attribute
        self.failUnless(admin.name == "Administrators")
        try:
            admin.description
        except PermissionDenied:
            pass
        else:
            self.failIf(True, "The private attribute has been read")   # Shouldn't reach there!
        
        
        
        