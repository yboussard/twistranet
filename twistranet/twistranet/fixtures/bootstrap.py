"""
The minimal bootstrap for TN to work.
We use a python file to ensure proper DB alimentation. Django fixtures are not enough to ensure DB consistancy.

Objects in those fixtures will get created but NEVER updated.
"""
from twistranet.twistranet.models import *
from twistranet.twistranet.lib.python_fixture import Fixture

FIXTURES = [
    Fixture(
        GlobalCommunity,
        slug = "all_twistranet",
        title = "All Twistranauts",
        description = "You can find all twistranauts in here. This community is a good place to start looking for people or for critical information about twistranet.",
        permissions = "intranet",
    ),
    Fixture(
        AdminCommunity,
        slug = "administrators",
        title = "Administrators",
        description = "TwistraNet admin team",
        permissions = "workgroup",
        publisher = GlobalCommunity.objects.filter(),
    ),

    # Default menu items
    Fixture(
        Menu,
        slug = "menu_main",
        title = "Main Menu",
        publisher = GlobalCommunity.objects.filter(),
    ),

    Fixture(
        MenuItem,
        parent = Menu.objects.filter(slug = "menu_main"),
        order = 0,
        view_path = "twistranet_home",
        title = "Home",
        slug = "menuitem_home",
        publisher = GlobalCommunity.objects.filter(),
    ),

    Fixture(
        MenuItem,
        parent = Menu.objects.filter(slug = "menu_main"),
        order = 10,
        view_path = 'communities',
        title = "Communities",
        slug = "menuitem_communities",
        publisher = GlobalCommunity.objects.filter(),
    ),

    Fixture(
        MenuItem,
        parent = MenuItem.objects.filter(slug = "menuitem_communities"),
        order = 0,
        view_path = 'communities',
        title = "View all communities",
        slug = "menuitem_all_communities",
        publisher = GlobalCommunity.objects.filter(),
    ),
    
]


