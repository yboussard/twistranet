"""
In this file you'll find functions used to load initial data in a safe and django way,
plus some tools to check and repair your DB.

See doc/DESIGN.txt for caveats about database
"""
import traceback

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User

from contentregistry import ContentRegistry
from content import Content, StatusUpdate
from account import Account, UserAccount, SystemAccount
from relation import Relation
from community import Community, GlobalCommunity, AdminCommunity
from resourcemanager import ResourceManager, ReadOnlyFilesystemResourceManager
from resource import Resource
import _permissionmapping
from twistranet.lib import permissions


def repair():
    """
    Repair a possibly damaged database.
    For example, incomplete fixtures can be a problem; use this to repair.
    We use that before launching tests. We should one day export a well-formed test fixture...
    
    Warning: can be very slow on a normal system!
    
    Will not erase data it doesn't know how to handle.
    """
    # Login
    __account__ = SystemAccount.objects.get()

    # Put all Django admin users inside the first admin community
    # and create accounts for them accordingly.
    django_admins = UserAccount.objects.filter(user__is_superuser = True)
    for user in django_admins:
        if not Community.objects.admin in user.my_communities:
            Community.objects.admin.join(user)
        
    # All user accounts must (explicitly) belong to the global community.
    # XXX There should be a more efficient way to do this ;)
    global_ = Community.objects.global_
    if UserAccount.objects.count() <> global_.members.count():
        # print "All accounts are not in the global comm. We manually add them"
        for account in UserAccount.objects.get_query_set():
            if global_ not in account.communities:
                # print "Force user %s to join global" % account
                global_.join(account)
                
    # XXX ULTRA ULTRA UGLY AND TEMPORARY: Enforce security update of all objects!
    for content in Content.objects.get_query_set():
        try:
            _permissionmapping._ContentPermissionMapping.objects._applyPermissionsTemplate(content, _permissionmapping._ContentPermissionMapping)
        except ValidationError:
            print "UNABLE TO SET SECURITY ON AN OBJECT. YOU MAY HAVE TO DELETE IT FROM THE SYSTEM ACCOUNT!"
            traceback.print_exc()
    for account in Account.objects.get_query_set():
        try:
            _permissionmapping._AccountPermissionMapping.objects._applyPermissionsTemplate(account, _permissionmapping._AccountPermissionMapping)
        except ValidationError:
            print "UNABLE TO SET SECURITY ON AN OBJECT. YOU MAY HAVE TO DELETE IT FROM THE SYSTEM ACCOUNT!"
            traceback.print_exc()
                
    # XXX TODO: Check if approved relations are symetrical


def bootstrap():
    """
    Load initial data if it's not present.
    This method is SAFE, ie. it won't destroy any existing data, only add missing stuff`.
    
    This should be called every time twistranet is started!
    """
    try:
        # Create the main system account if it doesn't exist
        try:
            __account__ = SystemAccount.objects.get()
        except ObjectDoesNotExist:
            _system = SystemAccount()
            __account__ = _system
            _system.permissions = "listed"
            _system.name = "TwistraNet System"
            _system.save()
        _system = SystemAccount.get()
    
        # Create the global community if it doesn't exist.
        try:
            global_ = Community.objects.global_
        except ObjectDoesNotExist:
            global_ = GlobalCommunity(
                name = "All TwistraNet Members",
                description = "This community contains all TwistraNet members. It's mainly used for critical information."
                )
            global_.permissions = "intranet"        # Default permissions = intranet
            global_.save()
    
        # Create the admin community if it doesn't exist.
        try:
            admincommunity = Community.objects.admin
        except ObjectDoesNotExist:
            c = AdminCommunity(
                name = "Administrators",
                description = "TwistraNet admin team",
                )
            c.permissions = "workgroup"
            c.save()
        admincommunity = Community.objects.admin
        
        # Create Legacy Resource Manager if doesn't exist.
        # If one exists it must be attach to no community.
        try:
            legacy_rm = ReadOnlyFilesystemResourceManager.objects.get()
        except ObjectDoesNotExist:
            legacy_rm = ReadOnlyFilesystemResourceManager(name = "Default TwistraNet resources")
            legacy_rm.save()
            
        # Load / Update default TN resource files
        legacy_rm.loadAll(with_aliases = True) 
            
        # Check default profile pictures
        profile_picture = Resource.objects.get(alias = "default_profile_picture")
        community_picture = Resource.objects.get(alias = "default_community_picture")
        a_picture = Resource.objects.get(alias = "default_a_picture")
        b_picture = Resource.objects.get(alias = "default_b_picture")
        admin_picture = Resource.objects.get(alias = "default_admin_picture")
        
        # Change A / B / TN profile pictures if they're not set
        print "change profile pictures"
        if UserAccount.objects.filter(name = 'admin').exists():
            print "admin"
            A = UserAccount.objects.get(name = 'admin')
            if not A._picture:
                A._picture = admin_picture
                A.save()
        if UserAccount.objects.filter(name = 'A').exists():
            A = UserAccount.objects.get(name = 'A')
            if not A._picture:
                A._picture = a_picture
                A.save()
        if UserAccount.objects.filter(name = 'B').exists():
            B = UserAccount.objects.get(name = 'B')
            if not B._picture:
                B._picture = b_picture
                B.save()
            
    except:
        print "UNABLE TO LOAD INITIAL DATA. YOUR SYSTEM IS IN AN UNSTABLE STATE."
        traceback.print_exc()
        
    else:
        # print "Initialized DB successfuly"
        pass
    
def check_consistancy():
    """
    Check DB consistancy.
    This method is SAFE (doesn't write anything) but is blocking if a problem is detected.
    """
    # XXX Check that there's 1! global community
    # XXX Check that there's 1! admin community
    
