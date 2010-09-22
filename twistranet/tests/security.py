"""
This is a basic wall test.
"""
from django.test import TestCase
from twistranet.models import *

class SecurityTest(TestCase):
    
    def setUp(self):
        """
        Get A and B users
        """
        dbsetup.load_initial_data()
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.PJ = UserAccount.objects.get(user__username = "pjgrizel").account_ptr
        self._system = SystemAccount.getSystemAccount()
        
    def test_has_system_account(self):
        """
        Is system account created and working?
        """
        system_accounts = SystemAccount.objects.all()
        self.failUnlessEqual(len(system_accounts), 1)
    
    
    def test_system_account(self):
        """
        Check if system account can access all communities
        """
        self.failUnlessEqual(
            len(Community._objects.all()),
            len(self._system.communities.all()),
            )
        
    def test_default_communities(self):
        """
        There should be one global com. and one member-only com.
        AND the system account must see them all.
        """
        self.failUnlessEqual(len(AdminCommunity._objects.filter(community_type = "AdminCommunity")), 1)
        self.failUnlessEqual(len(GlobalCommunity._objects.filter(community_type = "GlobalCommunity")), 1)
        self.failUnlessEqual(len(self._system.communities.admin), 1)
        self.failUnlessEqual(self._system.communities.global_.community_type, "GlobalCommunity")
        
    def test_communities(self):
        """
        Check if system is in the two communities
        """
        self.failUnlessEqual(len(self._system.communities.my), 1)
        self.failUnlessEqual(len(self._system.communities), 2)
        self.failUnlessEqual(len(self.A.communities.my), 1)
        
    def test_membership(self):
        self.failUnlessEqual(len(self.A.communities.my), 1)
        c = Community(
            name = "Test Community", 
            scope = "authenticated",
            )
        c.save()
        c.join(self.A)
        self.failUnless(self.A in c.members.all())
        self.failUnlessEqual(len(self.A.communities.my), 2)
        

