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

def bootstrap():
    """
    Load initial data if it's not present.
    This method is SAFE, ie. it won't destroy any existing data, only add missing stuff.
    """
    try:
        # Create the main system account if it doesn't exist
        try:
            __account__ = SystemAccount.objects.get()
        except ObjectDoesNotExist:
            _system = SystemAccount()
            _system.permissions = "listed"
            _system.save()
            __account__ = _system
        _system = SystemAccount.getSystemAccount()
    
        # Create the global community if it doesn't exist.
        try:
            global_ = Community.objects.global_
        except ObjectDoesNotExist:
            global_ = GlobalCommunity(
                name = "All TwistraNet Members",
                description = "This community contains all TwistraNet members. It's mainly used for critical information."
                )
            global_.permissions = "ou"
            global_.save()
    
        # Create the admin community if it doesn't exist.
        if not (Community.objects.admin):
            c = AdminCommunity(
                name = "TwistraNet admin team",
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
            
        # Check default profile picture
        profile_picture = Resource.objects.get(alias = "default_profile_picture")
            
        # Put all Django admin users inside the first admin community
        # and create accounts for them accordingly.
        django_admins = User.objects.filter(is_superuser = True)
        for user in django_admins:
            # XXX Check if this fails
            account = Account.objects.get(id = user.useraccount.id)
            
        # All accounts must (explicitly) belong to the global community.
        # XXX There should be a more efficient way to do this ;)
        if Account.objects.count() <> global_.members.count():
            # print "All accounts are not in the global comm. We manually add them"
            for account in Account.objects.get_query_set():
                if global_ not in account.communities:
                    # print "Force user %s to join global" % account
                    global_.join(account)
                    
        # Update accounts with no profile picture
        for nopicture in Account.objects.filter(picture = None):
            nopicture.picture = profile_picture
            nopicture.save()
                    
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
    
