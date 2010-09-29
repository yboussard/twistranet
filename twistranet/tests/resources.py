"""
This is a set of extensive resource management tests.
"""
from django.test import TestCase
from twistranet.models import *

class ResourcesTest(TestCase):
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
        self._system = __account__
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.PJ = UserAccount.objects.get(user__username = "pjgrizel").account_ptr
    

    def test_profile_picture(self):
        """
        Check if profile picture is publicly available
        """
        self.failUnless(self.A.picture)
        self.failUnless(self.B.picture)
        self.failUnless(self.PJ.picture)

    def test_public_resource(self):
        """
        Try to get a public resource anonymously.
        We fetch the first we can find
        """
        # Read the first public resource we can find
        r = Resource.objects.all()[0]
        self.failUnless(r.get().read())


