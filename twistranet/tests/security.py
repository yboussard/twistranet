"""
This is a basic wall test.
"""
from django.test import TestCase
from twistranet.models import *
from twistranet.lib import permissions, roles
from django.core.exceptions import ValidationError, PermissionDenied

from twistranet.lib import dbsetup, notifier

class SecurityTest(TestCase):
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
        
    def test_has_role(self):
        """
        Test various has_role conditions
        """
        __account__ = self.system
        obj = GlobalCommunity.objects.get()
        self.failUnless(self.system.has_role(roles.system, obj))
        self.failUnless(self.system.has_role(roles.administrator, obj))
        self.failIf(self.admin.has_role(roles.system, obj))
        self.failUnless(self.admin.has_role(roles.administrator, obj))
        self.failUnless(self.admin.has_role(roles.community_member, obj))
        self.failIf(self.admin.has_role(roles.community_manager, obj))
        
    def test_can_join(self,):
        """
        Check if can_join permissions seem ok.
        """
        __account__ = self.A
        adm = Community.objects.get(slug = "administrators")
        self.failIf(adm.can_join)
        self.failIf(adm.can_leave)
        __account__ = self.admin
        self.failUnless(adm.can_join)        
        self.failIf(adm.can_leave, "Administrator is the last account on this community, it shouldn't be able to leave")
    
    def test_can_edit(self,):
        """
        Check some basic edition rights
        """
        __account__ = self.A
        adm = Community.objects.get(slug = "administrators")
        self.failIf(adm.can_edit)
        __account__ = self.A
        self.failIf(adm.is_manager)
        self.failIf(adm.can_edit)
        __account__ = self.admin
        self.failUnless(adm.is_manager)
        self.failUnless(adm.can_edit)
    
    def test_private_content(self):
        """
        Check private content behavior
        """
        # A creates a private object
        __account__ = self.A
        s = StatusUpdate.objects.create(
            text = "Hello, World!",
            permissions = "private"
            )
        s.save()
        self.failUnless(s.content_ptr in Content.objects.all())
        
        # twistranet must not see it
        __account__ = self.admin
        self.failUnless(s.content_ptr not in Content.objects.all())
        
        # B must not see it
        __account__ = self.B
        self.failUnless(s.content_ptr not in Content.objects.all())
        
        # B creates a private object, same kind of tests
        __account__ = self.B
        s = StatusUpdate.objects.create(text = "Hello", permissions = "private")
        s.save()
        self.failUnless(s.content_ptr in Content.objects.all())
        __account__ = self.admin
        self.failUnless(s.content_ptr not in Content.objects.all())
        __account__ = self.A
        self.failUnless(s.content_ptr not in Content.objects.all())
        __account__ = self.B
        self.failUnless(s.content_ptr in Content.objects.all())
        
        # Oh, by the way, the system account must see 'em !
        __account__ = self.system
        self.failUnless(s.content_ptr in Content.objects.all())
        
    def test_network_content(self):
        """
        Check if network-protected content is accessible to NW only
        """
        __account__ = self.A
        s = StatusUpdate(text = "Hello, World!", permissions = "network")
        s.save()
        
        # Check if 'view' permission is ok in permissionmapping
        self.failUnless(s.content_ptr in Content.objects.all())
        __account__ = self.admin       # admin is in A's network
        self.failUnless(s.content_ptr in Content.objects.all())
        __account__ = self.B        # B is not
        self.failUnless(s.content_ptr not in Content.objects.all())
            
    # def test_silent_permissions(self):
    #     """
    #     Ensure permissions are not easily visible.
    #     XXX Disabled by now for simplicity reasons.
    #     """
    #     __account__ = self.A
    #     s = StatusUpdate(text = "Hello, World!", permissions = "network")
    #     s.save()
    #     self.failIf(s._permissions.filter(name = 'can_view').all())
    #     self.failIf(s._permissions.all())
        
            
    def test_public_content(self):
        """
        Check if public content on an account is visible by anyone
        """
        __account__ = self.A
        s = StatusUpdate(text = "Hello, World!", permissions = "public")
        s.save()
        self.failUnless(s.content_ptr in Content.objects.all())
        __account__ = self.admin       # admin is in A's network
        self.failUnless(s.content_ptr in Content.objects.all())
        __account__ = self.B        # B is not
        self.failUnless(s.content_ptr in Content.objects.all())
        
    def test_content_deletion(self):
        """
        Check if I can delete my own content
        """
        # I should be able to delete a content I wrote
        __account__ = self.A
        StatusUpdate(text = "Hi, there.").save()
        c = StatusUpdate.objects.filter(author = self.A)[0]
        _id = c.id
        c.delete()
        self.failIf(StatusUpdate.objects.filter(id = _id))
        
        # I shouldn't be able to delete a content I didn't write
        c = StatusUpdate.objects.filter(author = self.admin)[0]
        _id = c.id
        self.assertRaises(Exception, c.delete, ())
        self.failUnless(StatusUpdate.objects.filter(id = _id))
        
    def test_intranet_internet(self):
        """
        Check if anonymous can read public content on an internet mode.
        """
        # Default is intranet. Check that we have access to no content.
        self.failUnlessEqual(StatusUpdate.objects.count(), 0)
        
        # Become an internet. There should be some content available
        __account__ = self.system
        glob = GlobalCommunity.objects.get()
        glob.permissions = "internet"
        glob.save()
        del __account__
        self.failUnless(StatusUpdate.objects.count())

        # Get back to intranet. No more content please.
        __account__ = self.system
        glob = GlobalCommunity.objects.get()
        glob.permissions = "intranet"
        glob.save()
        del __account__
        self.failIf(StatusUpdate.objects.count())
        
    def test_hassystem_account(self):
        """
        Is system account created and working?
        """
        __account__ = self.system
        system_accounts = SystemAccount.objects.all()
        self.failUnlessEqual(len(system_accounts), 1)
    
    
    def testsystem_account(self):
        """
        Check if system account can access all communities
        """
        __account__ = self.system
        self.failUnlessEqual(len(Community.objects.all()), 2)
        
    def test_default_communities(self):
        """
        There should be one global com. and one member-only com.
        AND the system account must see them all.
        """
        __account__ = self.system
        self.failUnlessEqual(len(AdminCommunity.objects.filter(model_name = "AdminCommunity")), 1)
        self.failUnlessEqual(len(GlobalCommunity.objects.filter(model_name = "GlobalCommunity")), 1)
        self.failUnlessEqual(Community.objects.admin.model_name, "AdminCommunity")
        self.failUnlessEqual(Community.objects.global_.model_name, "GlobalCommunity")
        
    def test_communities(self):
        """
        Check if system is NOT in the community.
        """
        __account__ = self.system
        self.failUnlessEqual(len(self.system.communities), 0)
        self.failUnlessEqual(len(Community.objects.all()), 2)
        
    def test_membership(self):
        __account__ = self.system
        self.failUnlessEqual(len(self.A.communities), 1)
        c = Community.objects.create(title = "Test Community", permissions = "ou")
        c.save()
        c.join(self.A)
        self.failUnless(self.A in c.members.all())
        self.failUnlessEqual(len(self.A.communities), 2)
        
        
    def test_can_view(self):
        """
        Check if can_view permission works as expected
        """
        __account__ = self.B
        self.B.permissions = "listed"
        self.B.save()
        hello = StatusUpdate(text = "Hello there", permissions = "public")
        hello.save()
        self.failUnless(hello.can_view)
        
    def test_notification(self):
        """
        Check if a notification for B is seen only by those who can see B
        """
        __account__ = self.B
        self.B.permissions = "listed"
        self.B.save()
        hello = StatusUpdate(text = "Hello there", permissions = "public")
        hello.save()
        n = notifier.likes(self.B, hello)
        nid = n.id
        self.failUnless(Content.objects.filter(id = nid).exists())
        __account__ = self.A
        self.failIf(Content.objects.filter(id = nid).exists())
        





