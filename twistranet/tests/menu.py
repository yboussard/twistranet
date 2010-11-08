"""

Test basic menu features.
"""
from django.test import TestCase
from twistranet.models import *
from twistranet.lib import dbsetup

class MenuTest(TestCase):
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
        self._system = __account__
        self.B = UserAccount.objects.get(user__username = "B").account_ptr
        self.A = UserAccount.objects.get(user__username = "A").account_ptr
        self.admin = UserAccount.objects.get(user__username = "admin").account_ptr

    def test_menu_creation(self):
        """
        Create a menu and test if it's available
        """
        __account__ = self.admin
        c = Community(
            screen_name = "Test community",
            permissions = "private",
            )
        c.save()
        cid = c.id
        menu = Menu(
            slug = "test",
            name = "Test Menu",
            )
        menu.save()
        
        # Create some menu items
        item = MenuItem(
            menu = menu,
            order = 0,
            title = None,
            )
        item.target = c
        item.save()
        self.failUnless(cid in [ item.target_id for item in menu.children ])
        
        # Check if sbd who can't see the community can't access the menu
        __account__ = self.A
        self.failIf(cid in [ item.target_id for item in menu.children ])
        
    def test_public_resource(self):
        """
        Try to get a public resource anonymously.
        We fetch the first we can find
        """
        # Get the first public resource
        r = Resource.objects.all()[0]
        self.failUnless(r.get())


