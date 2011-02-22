"""

Test basic menu features.
"""
from twistranet.twistapp.tests.base import TNBaseTest
from twistranet.twistapp.models import *
from twistranet.content_types import *
from twistranet.core import bootstrap

class MenuTest(TNBaseTest):
    """
    Just to remember:
    A <=> admin
    B  => admin
    """
    


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
        

