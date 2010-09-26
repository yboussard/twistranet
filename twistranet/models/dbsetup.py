"""
In this file you'll find functions used to load initial data in a safe and django way,
plus some tools to check and repair your DB.

See doc/DESIGN.txt for caveats about database
"""
import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from contentregistry import ContentRegistry
from content import Content, StatusUpdate
from account import Account, UserAccount, SystemAccount
from relation import Relation
from community import Community, GlobalCommunity, AdminCommunity
from scope import *

def load_initial_data():
    """
    Load initial data if it's not present.
    This method is SAFE, ie. it won't destroy any existing data, only add missing.
    """
    try:
        # Create the main system account if it doesn't exist
        try:
            __account__ = SystemAccount.objects.get()
        except:
            _system = SystemAccount()
            _system.scope = ACCOUNTSCOPE_ANONYMOUS
            _system.save()
            __account__ = _system
        _system = SystemAccount.getSystemAccount()
    
        # Create the global community if it doesn't exist.
        try:
            global_ = Community.objects.global_
        except ObjectDoesNotExist:
            global_ = GlobalCommunity(
                name = "All TwistraNet Members",
                )
            global_.scope = ACCOUNTSCOPE_AUTHENTICATED
            global_.save()
    
        # Create the admin community if it doesn't exist.
        if not (Community.objects.admin):
            c = AdminCommunity(
                name = "TwistraNet admin team",
                )
            c.scope = ACCOUNTSCOPE_MEMBERS
            c.save()
        admincommunity = Community.objects.admin
            
        # Put all Django admin users inside the first admin community
        # and create accounts for them accordingly.
        django_admins = User.objects.filter(is_superuser = True)
        for user in django_admins:
            # XXX Check if this fails
            account = Account.objects.get(id = user.useraccount.id)
            
        # All accounts must (explicitly) belong to the global community.
        # There should be a better way to do this ;)
        if Account.objects.count() <> global_.members.count():
            # print "All accounts are not in the global comm. We manually add them"
            for account in Account.objects.get_query_set():
                if global_ not in account.communities:
                    # print "Force user %s to join global" % account
                    global_.join(account)
                    
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
    
