"""
This is a set of account permissions tests
"""
from django.test import TestCase
from twistranet.models import *
from twistranet.lib import permissions, roles
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError

from twistranet.lib import dbsetup

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
        dbsetup.repair()
        __account__ = SystemAccount.get()
        self.system = __account__
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.PJ = UserAccount.objects.get(user__username = "admin").account_ptr
        self.admin = self.PJ
    
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
        
    def test_account_network_role(self):
        """
        Check if A and admin have the account_network role on each other
        """
        __account__ = self.admin
        self.failUnless(self.admin.has_role(roles.account_network, self.A))
        self.failIf(self.admin.has_role(roles.account_network, self.B))
        
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
        
        
    def test_slugify(self):
        """
        Test if slugify works. Check slugification and check against duplicates
        """
        __account__ = self.admin
        c = Community()
        c.title = u"My @\xc3\xa2 Community ! It has a very long title so it's going to be heavily sluggified!"
        c.save()
        self.failUnlessEqual(c.slug, "my_a_community_it_has_a_very_long_title_so_its_goi")
        c = Community()
        c.title = u"My @\xc3\xa2 Community ! It has a very long title so it's going to be heavily sluggified!"
        try:
            c.save()
        except:
            pass
        else:
            self.fail("Should have been raising as the two slugs are identical!")
        
        
        
    def test_cant_view_attributes(self):
        """
        Fetch a restricted account and check if we can't read basic properties.
        In our example we use the 'admin' community, which is listed but can't be viewed.
        """
        # Check if we find the admin community
        __account__ = self.A
        admin = Community.objects.get(slug = "administrators")
        self.failIf(admin.can_view)

        # Create a community and perform the same kind of checks
        c = Community.objects.create(slug = "My Workgroup", permissions = "workgroup")
        c.save()
        self.failUnless(c.can_view)
        __account__ = self.B
        self.failIf(c.can_view)
        __account__ = self.PJ
        self.failIf(c.can_view)
        
        # Check community slug, then the protected 'description' attribute
        # DISABLED FOR PERFORMANCE REASONS
        # self.failUnless(admin.slug == "Administrators")
        # try:
        #     admin.description
        # except PermissionDenied:
        #     pass
        # else:
        #     self.failIf(True, "The private attribute has been read")   # Shouldn't reach there!
        
    def test_can_publish(self):
        """
        Check if the can_publish attribute works
        """
        # Must be able to write on self.
        # Friends (in the network) can also write on one's wall!
        __account__ = self.A
        self.failUnless(self.A.can_publish)
        self.failIf(self.B.can_publish)
        self.failUnless(self.admin.can_publish)
        
        # Try to write on a wg community
        c = Community(slug = "wkg", permissions = "workgroup")
        c.save()
        self.failUnless(c.can_publish)
        __account__ = self.B
        self.failIf(c.can_publish)
        __account__ = self.A
        c.join(self.B)
        __account__ = self.B
        self.failUnless(c.can_publish)
        
        # Try to publish on an 'ou' community as a simple member ; must be forbidden
        __account__ = self.A
        c = Community(slug = "ou", permissions = "ou")
        c.save()
        self.failUnless(c.can_publish)
        __account__ = self.B
        self.failIf(c.can_publish)
        __account__ = self.A
        c.join(self.B)
        __account__ = self.B
        self.failIf(c.can_publish)
        
        
    def test_community_creation(self):
        """
        We create a community and check basic stuff
        """
        __account__ = self.A
        c = Community.objects.create(slug = "My Workgroup", permissions = "workgroup")
        c.save()
        self.failUnless(c.can_view)
        self.failUnless(c.is_manager)
        c_id = c.id
        
        # B can LIST but can't VIEW the community by now (neither PJ)
        __account__ = self.B
        self.failUnless(Community.objects.filter(id = c_id).exists())
        self.failIf(c.can_view)
        __account__ = self.PJ
        self.failUnless(Community.objects.filter(id = c_id).exists())
        self.failIf(c.can_view)
        
        # We add B inside, B should see it
        __account__ = self.A
        c.join(self.B)
        self.failUnless(self.B in c.members.all())
        __account__ = self.B
        self.failUnless(Community.objects.filter(id = c_id).exists())
        self.failUnless(c.is_member)
        self.failIf(c.is_manager)
        
        