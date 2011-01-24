"""
This is a set of account permissions tests
"""
import pprint
from django.test import TestCase
from django_twistranet.models import *
from django_twistranet.lib import permissions, roles
from django_twistranet.content_types import *
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError

from django_twistranet.lib import dbsetup

class AccountSecurityTest(TestCase):
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
        self.A = UserAccount.objects.get(user__username = "A")
        self.B = UserAccount.objects.get(user__username = "B")
        self.C = UserAccount.objects.get(user__username = "C")
        self.admin = UserAccount.objects.get(user__username = "admin")
        
    def test_00_bootstrap_objects(self,):
        """
        Test owner and publisher of various bootstrap objects.
        """
        __account__ = self.system
        self.failUnless(self.system.publisher == None, "SystemAccount must be visible to anon. for TN to work.")
        self.failUnless(self.system.owner.id == self.system.id, "SystemAccount must own itself")
        glob = GlobalCommunity.objects.get()
        admin = Community.objects.get(slug = "administrators")
        self.failUnlessEqual(glob.publisher.id, glob.id)
        self.failUnlessEqual(glob.owner.id, admin.id, "Global community must be own by the Admin Community, not %s" % glob.owner)
        self.failUnlessEqual(admin.publisher.id, glob.id, "Admin community must be published on Global (at least by default)")
        self.failUnlessEqual(admin.owner.id, self.system.id, "Admin community must be own by the SystemAccount.")
        self.failUnlessEqual(self.A.publisher.id, glob.id, "Default users must be published on the global community (instead of %s)" % self.A.publisher)
        self.failUnlessEqual(self.B.publisher.id, glob.id, "Default users must be published on the global community")
        self.failUnlessEqual(self.A.owner.id, self.system.id, )
        self.failUnlessEqual(self.B.owner.id, self.system.id, )
    
    def test_01_default_owner_publisher(self):
        """
        Check that default options for owner and publisher attributes are ok
        """
        from django.contrib.auth.models import User
        __account__ = self.A
        glob = GlobalCommunity.objects.get()
        admin = Community.objects.get(slug = "administrators")
        obj = Document.objects.create(text = "hi, there.")
        obj.save()
        self.failUnlessEqual(obj.owner.id, self.A.id, "An object must be own by its creator by default.")
        self.failUnlessEqual(obj.publisher.id, self.A.id, "An object must be published on its creator by default.")
        u = User.objects.create(username = "test")
        obj = UserAccount.objects.create(slug = "test_account", user = u)
        # self.failUnlessEqual(obj.owner.id, admin.id, "A UserAccount must be own by the admin community by default.")
        self.failUnlessEqual(obj.publisher.id, glob.id, "A UserAccount must be published on the global community by default.")
        obj = Community.objects.create(slug = "test_community")
        obj.save()
        self.failUnlessEqual(obj.owner.id, self.A.id, "A community must be own by its creator by default.")
        self.failUnlessEqual(obj.publisher.id, self.A.id, "A community must be published on its creator by default.")
    
    def test_02_basic_listing(self):
        """
        Check if I can see myself and the global community
        """
        self.failIf(GlobalCommunity.objects.exists(), "Default is to have the global community invisible (intranet mode)")
        __account__ = self.A
        self.failUnless(self.A in UserAccount.objects.all())
        self.failUnless(GlobalCommunity.objects.exists())
        self.failIf(self.C in UserAccount.objects.all())
        __account__ = self.B
        self.failUnless(self.B in UserAccount.objects.all()) 
        self.failUnless(GlobalCommunity.objects.exists())
        self.failIf(self.C in UserAccount.objects.all())
        __account__ = self.admin
        self.failUnless(self.admin in UserAccount.objects.all()) 
        self.failUnless(GlobalCommunity.objects.exists())
        self.failUnless(self.A in UserAccount.objects.all())
        self.failUnless(self.B in UserAccount.objects.all())
        # self.failUnless(self.C in UserAccount.objects.all())  XXX Removed now 'cause admin members can't see private accounts.
        __account__ = self.C
        self.failUnless(self.A in UserAccount.objects.all())
        self.failUnless(GlobalCommunity.objects.exists())
        self.failUnless(self.C in UserAccount.objects.all())
        
    def test_02_private_account(self):
        """
        Check if I can make an account private.
        Note that private accounts are still visible in their network!
        """
        __account__ = self.A
        self.failUnless(self.A in UserAccount.objects.all()) 
        self.A.permissions = "private"
        self.A.save()
        self.failUnless(self.A in UserAccount.objects.all()) 
        __account__ = self.B
        self.failIf(self.A in UserAccount.objects.all(), "A is private, so B should not see it anymore.")
        __account__ = self.admin
        self.failUnless(self.A in UserAccount.objects.all(), "A private account must still be listable in its network")
        
    def test_03_listed_account(self,):
        """
        Ensure that a listed account is visible
        """
        __account__ = self.B
        self.failUnless(self.B in UserAccount.objects.all(), "B should be able to see itself")
        __account__ = self.admin
        self.failUnless(self.B in UserAccount.objects.all(), "admin should be able to see (listed) B")
        __account__ = self.A
        self.failUnless(self.B in UserAccount.objects.all(), "A should be able to see (listed) B")
        
        
    def test_04_account_network_role(self):
        """
        Check if A and admin have the network role on each other.
        As B requested access to admin, admin should be automatically given the 'network' role to B.
        """
        __account__ = self.admin
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        self.failUnless(self.admin.has_role(roles.network, A))
        self.failUnless(self.admin.has_role(roles.network, B))
        __account__ = self.A
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        self.failUnless(self.A.has_role(roles.network, admin))
        __account__ = self.B
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        self.failIf(self.B.has_role(roles.network, admin))
        
        # Check objects of a different class as well
        __account__ = self.admin
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        self.failUnless(self.admin.account.has_role(roles.network, A))
        self.failUnless(self.admin.has_role(roles.network, B.account))
        __account__ = self.A
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        self.failUnless(self.A.account.has_role(roles.network, admin))
        __account__ = self.A.account
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        self.failUnless(self.A.has_role(roles.network, admin))
        __account__ = self.B
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        self.failIf(self.B.has_role(roles.network, admin.account))
        
    def test_05_cant_view_attributes(self):
        """
        Fetch a restricted account and check if we can't read basic properties.
        In our example we use the 'admin' community, which is listed but can't be viewed.
        """
        # Check if we find the admin community
        __account__ = self.A
        admin = Community.objects.get(slug = "administrators")
        self.failIf(admin.can_view)

        # Create a community and perform the same kind of checks
        c = Community.objects.create(slug = "MyWorkgroup", permissions = "workgroup")
        c.save()
        self.failUnless(c.can_view)
        __account__ = self.B
        self.failIf(c.can_view)
        # Admin should be owner of the newborn community (or not)
        __account__ = self.admin
        self.failIf(c.can_view)
                
    def test_06_can_publish(self):
        """
        Check if the can_publish attribute works
        """
        # Must be able to write on self.
        # Friends (in the network) can also write on one's wall!
        __account__ = self.A
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        self.failUnless(A.can_publish)
        self.failIf(B.can_publish)
        self.failUnless(admin.can_publish)
        
        # Try to write on a wg community
        c = Community(slug = "wkg", permissions = "workgroup")
        c.save()
        self.failUnless(c.can_publish)
        __account__ = self.B
        c = Community.objects.get(slug = "wkg")
        self.failIf(c.can_publish)
        __account__ = self.A
        c = Community.objects.get(slug = "wkg")
        c.join(self.B)
        # We re-load B so that its cache will be refreshed
        self.B = UserAccount.objects.get(slug = "B")
        __account__ = self.B
        c = Community.objects.get(slug = "wkg")
        self.failUnless(c.can_publish)
        
        # Try to publish on an 'ou' community as a simple member ; must be forbidden
        __account__ = self.A
        c = Community(slug = "ou", permissions = "ou")
        c.save()
        self.failUnless(c.can_publish)
        self.B = UserAccount.objects.get(slug = "B")
        __account__ = self.B
        c = Community.objects.get(slug = "ou")
        self.failIf(c.can_publish)
        __account__ = self.A
        c = Community.objects.get(slug = "ou")
        c.join(self.B)
        __account__ = self.B
        c = Community.objects.get(slug = "ou")
        self.failIf(c.can_publish)
        
    def test_07_community_creation(self):
        """
        We create a community and check basic stuff
        """
        __account__ = self.A
        c = Community.objects.create(slug = "MyWorkgroup", permissions = "workgroup")
        c.save()
        self.failUnless(c.can_view)
        self.failUnless(c.is_manager)
        c_id = c.id
        
        # B can LIST but can't VIEW the community by now (neither admin)
        __account__ = self.B
        self.failUnless(Community.objects.filter(id = c_id).exists())
        self.failIf(c.can_view)
        __account__ = self.admin
        self.failUnless(Community.objects.filter(id = c_id).exists())
        self.failIf(c.can_view)     # May or may not work depending on the security model
        
        # We add B inside, B should see it
        __account__ = self.A
        c.join(self.B)
        self.failUnless(self.B.account_ptr in c.members.all())
        __account__ = self.B
        self.failUnless(Community.objects.filter(id = c_id).exists())
        self.failUnless(c.is_member)
        self.failIf(c.is_manager)
        
        
    def test_08_private_community(self,):
        """
        Check if admin can see its own private communities
        """
        __account__ = self.admin
        c = Community.objects.create(
            title = "Test community",
            permissions = "private",
            )
        c.save()
        self.failUnless(c in Community.objects.all(), "A private community should be visible by its owner")
        
    def test_09_content_indirection(self,):
        """Check if I can reach a content by its publisher
        """
        __account__ = self.A
        c = Community.objects.create(
            title = "Test community",
            permissions = "private",
        )
        c.save()
        self.failUnlessEqual(self.A.id, c.owner.id, "A should be the community owner as it created it.")
        Document.objects.create(slug = "c_status", text = "coucou", publisher = c).save()
        self.failUnless(Content.objects.filter(slug = "c_status"), "I should see the status update I created on the community I own")
        
    def test_10_slugify(self):
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



        
        