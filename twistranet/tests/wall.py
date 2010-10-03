"""
This is a basic wall test.
"""
from django.test import TestCase
from twistranet.models import *

class SimpleTest(TestCase):
    
    def setUp(self):
        """
        Get A and B users
        """
        dbsetup.bootstrap()
        dbsetup.repair()
        __account__ = SystemAccount.get()
        self._system = __account__
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.PJ = UserAccount.objects.get(user__username = "pjgrizel").account_ptr
        
    def test_followed_private_content(self):
        """
        A and PJ are in the same network.
        If A creates a private, it must not be visible in PJ's wall (even with A account)
        """
        __account__ = self.A
        s = StatusUpdate(text = "Private", permissions = "private")
        s.save()
        self.failUnless(s.content_ptr in Content.objects.all())
        self.failUnless(s.content_ptr in Content.objects.followed.all())
        self.failUnless(s.content_ptr not in Content.objects.getFollowedBy(self.PJ).all())
        
    def test_followed_content_availability(self):
        """
        Check if public content is available in the other walls.
        We check everything from A's eyes
        """
        # Check networked content availability
        __account__ = self.A
        s = StatusUpdate(text = "NWK", permissions = "network")
        s.save()
        self.failUnless(s.content_ptr in Content.objects.all())
        self.failUnless(s.content_ptr in Content.objects.followed.all())        # Do I follow my own content?
        self.failUnless(s.content_ptr in Content.objects.getFollowedBy(self.A).all())
        self.failUnless(s.content_ptr in Content.objects.getFollowedBy(self.PJ).all())
        self.failUnless(s.content_ptr not in Content.objects.getFollowedBy(self.B).all())
        
        # Check public content availability
        s = StatusUpdate(text = "PUB", permissions = "public")
        s.save()
        self.failUnless(s.content_ptr in Content.objects.all())
        self.failUnless(s.content_ptr in Content.objects.followed.all())
        self.failUnless(s.content_ptr in Content.objects.getFollowedBy(self.A).all())
        self.failUnless(s.content_ptr in Content.objects.getFollowedBy(self.PJ).all())
        self.failUnless(s.content_ptr not in Content.objects.getFollowedBy(self.B).all())
        
        
    def test_simple_wall(self):
        """
        We look at B's wall and perform some actions to see what's going on.
        We use the default fixture to check stuff.
        """
        self.failUnlessEqual(self.B.useraccount.user.username, "B")
        
        # Check public objects. Must be empty (unless I put truly public objects in the fixture?)
        __account__ = None
        public_list = Content.objects.all()
        self.failUnlessEqual(len(public_list), 0)

        # Check wall objects. First one should be older than, say, the third one.
        __account__ = self.B
        latest = self.B.content.all().order_by('-date')[:5]
        self.failUnlessEqual(len(latest), 5)
        self.failUnless(latest[0].date >= latest[3].date, "Invalid date order for the wall")
        
    def test_wall_security(self):
        """
        Ensure that two users cannot see each other's 
        """
        # A creates a private content. B shouldn't see it.
        from twistranet.models import StatusUpdate
        __account__ = self.B
        b_initial_list = self.B.content.all()
        b_initial_followed = self.B.content.followed.all()
        
        # Test content creation
        __account__ = self.A
        s = StatusUpdate.objects.create()
        s.text = "Hello, this is A speaking"
        s.permissions = "private"
        s.save()
        self.failUnlessEqual(s.author, self.A)
        self.failUnlessEqual(s.publisher, self.A)
        
        # Check if B can see A's content (it shouldn't, as it's private
        __account__ = self.B
        b_final_list = self.B.content.all()
        self.failUnlessEqual(len(b_initial_list), len(b_final_list))
        
        # A creates / edits public content. B should see it even if he doesn't follow A
        __account__ = self.A
        s.permissions = "public"
        s.save()
        __account__ = self.B
        b_final_list = self.B.content.all()
        self.failUnlessEqual(len(b_initial_list) + 1, len(b_final_list))

        # ...but that shouldn't change anything for followed content
        self.failUnless(self.A not in self.B.getMyFollowed())
        self.failUnless(self.PJ in self.B.getMyFollowed())
        b_final_followed = self.B.content.followed
        self.failUnlessEqual(len(b_initial_followed), len(b_final_followed))

    def test_my_content(self):
        """
        Check if content I write is displayed
        """
        from twistranet.models import StatusUpdate
        __account__ = self.A
        s = StatusUpdate.objects.create()
        s.text = "Hello, this is A speaking"
        s.permissions = "private"
        s.save()
        self.failUnless(s.content_ptr in self.A.content.all())
        self.failUnless(s.content_ptr not in Content.objects.getFollowedBy(self.B))
        
        
        
        