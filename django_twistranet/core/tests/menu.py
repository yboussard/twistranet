"""

Test basic menu features.
"""
from django.test import TestCase
from twistranet.twistranet.models import *
from twistranet.content_types import *
from twistranet.twistranet.lib import dbsetup

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


    def test_01_regular_menu_creation(self):
        """
        Create a menu and test if it's available
        """
        __account__ = self.admin
        menu = Menu.objects.create(
            slug = "test",
            title = "Test Menu",
            )
        item = MenuItem.objects.create(
            parent = menu,
            slug = "menuitem",
            order = 0,
            link_url = "http://www.google.com",
            title = "",
            )
        self.failUnless(item in menu.children, "A menu item must appear in its children")

        # Check if sbd else can see the menu (they're public by default)
        __account__ = self.A
        self.failUnless(Menu.objects.filter(slug = 'test').exists())
        self.failUnless(MenuItem.objects.filter(slug = "menuitem").exists())
        item = MenuItem.objects.get(slug = "menuitem")
        self.failUnless(item in Menu.objects.get(slug = 'test').children)

    def test_02_menu_creation(self):
        """
        Create a menu and test if it's available
        """
        __account__ = self.admin
        c = Community.objects.create(
            title = "Test community",
            permissions = "private",
            )
        c.save()
        cid = c.id
        menu = Menu(
            slug = "test",
            title = "Test Menu",
            )
        menu.save()
        
        # Create some menu items
        item = MenuItem.objects.create(
            parent = menu,
            order = 0,
            title = "",
            target = c,
            )
        item.save()
        self.failUnless(item in menu.children, "A menu item must appear in its children")
        self.failUnless(cid in [ item.target_id for item in menu.children ], "The target must be visible in menu's children")
        
        # Check that sbd who can't see the community can't access the menu
        __account__ = self.A
        self.failIf(cid in [ item.target_id for item in menu.children ])
        

