"""
In this file you'll find functions used to load initial data in a safe and django way,
plus some tools to check and repair your DB.

See doc/DESIGN.txt for caveats about database
"""
import traceback

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User
from django.db.utils import DatabaseError

from twistranet.models import *
from twistranet.models import _permissionmapping
from twistranet.lib import permissions

from twistranet.fixtures.bootstrap import FIXTURES as BOOTSTRAP_FIXTURES
from twistranet.fixtures.help_en import FIXTURES as HELP_EN_FIXTURES

import settings

def repair():
    """
    Repair a possibly damaged database.
    For example, incomplete fixtures can be a problem; use this to repair.
    We use that before launching tests. We should one day export a well-formed test fixture...
    
    Warning: can be very slow on a normal system!
    
    Will not erase data it doesn't know how to handle.
    """
    # # Login
    __account__ = SystemAccount.objects.get()

    # Put all Django admin users inside the first admin community
    django_admins = UserAccount.objects.filter(user__is_superuser = True)
    for user in django_admins:
        if not Community.objects.admin in user.my_communities:
            Community.objects.admin.join(user, manager = True)
    #     
    # # All user accounts must (explicitly) belong to the global community.
    # # XXX There should be a more efficient way to do this ;)
    # global_ = Community.objects.global_
    # if UserAccount.objects.count() <> global_.members.count():
    #     # print "All accounts are not in the global comm. We manually add them"
    #     for account in UserAccount.objects.get_query_set():
    #         if global_ not in account.communities:
    #             # print "Force user %s to join global" % account
    #             global_.join(account)
    #             
    # # XXX ULTRA ULTRA UGLY AND TEMPORARY: Enforce security and cache
    # for content in Content.objects.get_query_set():
    #     content.object.save()
    #     # try:
    #     #     _permissionmapping._ContentPermissionMapping.objects._applyPermissionsTemplate(content.object)
    #     # except ValidationError:
    #     #     print "UNABLE TO SET SECURITY ON AN OBJECT. YOU MAY HAVE TO DELETE IT FROM THE SYSTEM ACCOUNT!"
    #     #     traceback.print_exc()
    # for account in Account.objects.get_query_set():
    #     try:
    #         _permissionmapping._AccountPermissionMapping.objects._applyPermissionsTemplate(account.object)
    #     except ValidationError:
    #         print "UNABLE TO SET SECURITY ON AN OBJECT. YOU MAY HAVE TO DELETE IT FROM THE SYSTEM ACCOUNT!"
    #         traceback.print_exc()
    #             
    # # XXX TODO: Check if approved relations are symetrical



def bootstrap():
    """
    Load initial data if it's not present.
    This method is SAFE, ie. it won't destroy any existing data, only add missing stuff`.
    
    This should be called every time twistranet is started!
    """
    try:
        # Let's log in.
        __account__ = SystemAccount.get()
    except ObjectDoesNotExist, DatabaseError:
        # Default fixture probably not installed yet. Don't do anything yet.
        print "DatabaseError while bootstraping. Your tables are probably not created yet."
        # traceback.print_exc()
        return
    
    # Create Legacy Resource Manager if doesn't exist.
    # If one exists it must be attach to no community.
    # We save back the __account__ system object to ensure proper resource loading
    try:
        legacy_rm = ReadOnlyFilesystemResourceManager.objects.get()
    except ObjectDoesNotExist:
        legacy_rm = ReadOnlyFilesystemResourceManager(name = "Default TwistraNet resources")
        legacy_rm.save()
    legacy_rm.loadAll(with_slug = True)
    __account__.save()
        
    # Now create the bootstrap / default / help fixture objects.
    for obj in BOOTSTRAP_FIXTURES:
        obj.apply()
        
    for obj in HELP_EN_FIXTURES:
        obj.apply()
        
    # Sample data only imported if asked to in settings.py
    if settings.TWISTRANET_IMPORT_SAMPLE_DATA:
        from twistranet.fixtures.sample import FIXTURES as SAMPLE_DATA_FIXTURES
        for obj in SAMPLE_DATA_FIXTURES:
            obj.apply()
        
        # Add relations bwn users
        # A <=> admin
        # B  => admin
        A = UserAccount.objects.get(slug = "A")
        B = UserAccount.objects.get(slug = "B")
        admin = UserAccount.objects.get(slug = "admin")
        A.follow(admin)
        admin.follow(A)
        B.follow(admin)
        
        # Check default profile pictures
        profile_picture = Resource.objects.get(slug = "default_profile_picture")
        community_picture = Resource.objects.get(slug = "default_community_picture")

        # Change A / B / TN profile pictures if they're not set
        admin.picture = Resource.objects.get(slug = "default_admin_picture")
        admin.save()
        A.picture = Resource.objects.get(slug = "default_a_picture")
        A.save()
        B.picture = Resource.objects.get(slug = "default_b_picture")
        B.save()            

    # Create the main menu manager and main menu items. Create help menu structure as well.
    try:
        menu = Menu.objects.get(slug = "main")
    except ObjectDoesNotExist:
        menu = Menu(
            slug = "main",
            name = "Main Menu",
            )
        menu.save()
        
        # Create default menu items
        item = MenuItem(
            menu = menu,
            order = 0,
            view_path = "twistranet.views.home",
            title = "Home",
            )
        item.save()
        item = MenuItem(
            menu = menu,
            order = 10,
            view_path = 'twistranet.views.communities',
            title = "Communities",
            )
        item.save()
        subitem = MenuItem(
            menu = menu,
            parent = item,
            order = 0,
            view_path = 'twistranet.views.communities',
            title = "View all communities",
            )
        subitem.save()
        subitem = MenuItem(
            menu = menu,
            parent = item,
            order = 10,
        )
        subitem.target = Community.objects.admin
        subitem.save()
        
    # Create / update the menu items
    # XXX TODO: use help_en.MENU_STRUCTURE
    # for obj in help_objects.values():
    #     try:
    #         item = MenuItem.objects.get(slug = obj.slug)
    #     except ObjectDoesNotExist:
    #         item = MenuItem(
    #             menu = menu,
    #             order = 90,
    #             title = "Help",
    #             slug = obj.slug,
    #             )
    #         item.target = obj
    #         item.save()
        
    
def check_consistancy():
    """
    Check DB consistancy.
    This method is SAFE (doesn't write anything) but is blocking if a problem is detected.
    """
    # XXX Check that there's 1! global community
    # XXX Check that there's 1! admin community
    
