"""
In this file you'll find functions used to load initial data in a safe and django way,
plus some tools to check and repair your DB.

See doc/DESIGN.txt for caveats about database
"""
import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from content import Content, StatusUpdate, ContentRegistry
from account import Account, UserAccount, SystemAccount
from relation import Relation
from community import Community, GlobalCommunity, AdminCommunity

def load_initial_data():
    """
    Load initial data if it's not present.
    This method is SAFE, ie. it won't destroy any existing data, only add missing.
    """
    try:
        # Create the main system account if it doesn't exist
        system_accounts = SystemAccount.objects.all()
        if len(system_accounts) == 0:
            _system = SystemAccount()
            _system.save()
        _system = SystemAccount.getSystemAccount()
    
        # Create the global community if it doesn't exist.
        try:
            g = _system.communities.global_
        except ObjectDoesNotExist:
            c = GlobalCommunity(
                name = "All TwistraNet Members",
                scope = "authenticated",
                )
            c.save()
    
        # Create the admin community if it doesn't exist.
        if not (_system.communities.admin):
            c = AdminCommunity(
                name = "TwistraNet admin team",
                scope = "members",
                )
            c.save()
        admincommunity = _system.communities.admin[0]
            
        # Put all Django admin users inside the first admin community
        # and create accounts for them accordingly.
        django_admins = User.objects.filter(is_superuser = True)
        for user in django_admins:
            # XXX Check if this fails
            account = user.useraccount
        
    except:
        print "UNABLE TO LOAD INITIAL DATA. YOUR SYSTEM IS IN AN UNSTABLE STATE."
        traceback.print_exc()
        
    else:
        print "Initialized DB successfuly"
    
def check_consistancy():
    """
    Check DB consistancy.
    This method is SAFE (doesn't write anything) but is blocking if a problem is detected.
    """
    # XXX Check that there's 1! global community
    # XXX Check that there's 1! admin community
    
