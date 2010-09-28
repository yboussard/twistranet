from django.db import models
from django.contrib.auth.models import User

import basemanager
from resource import Resource
from accountregistry import AccountRegistry
from twistranet.lib import permissions, roles

class AccountManager(basemanager.BaseManager):
    """
    This manager is used for secured account.
    """

    def get_query_set(self):
        """
        Return a queryset of 100%-authorized objects.
        """
        # Check for anonymous query
        authenticated = self._getAuthenticatedAccount()
        base_query_set = super(AccountManager, self).get_query_set()
        if not authenticated:
            # TODO: Return only anonymous objects and system accounts
            return base_query_set.filter(account_type = "SystemAccount")   # XXX BAD !!!

        # System account: return all objects
        if authenticated.account_type == "SystemAccount":
            authenticated.systemaccount   # This is one more security check, will raise if DB is not properly set
            return base_query_set       # The base qset with no filter

        # Account filter
        # TODO: Return only listed objects
        return base_query_set



# Create your models here.
class Account(models.Model):
    """
    A generic account.
    This is an abstract class.
    Can be subclassed as a user account, group account, app account, etc
    """
    # XXX Should hold:
    # An unique ID
    # A picture
    # A friendly name
    # name = models.CharField(max_length = 127)
    account_type = models.CharField(max_length = 64)
    picture = models.ForeignKey("Resource", null = True)    # Ok, this is odd... We'll avoid the 'null' attribute someday.
    objects = AccountManager()

    # Security models available for the user
    # XXX TODO: Use a foreign key instead with some clever checking? Or a specific PermissionField?
    # XXX because there's a problem here as choices cannot be re-defined for subclasses.
    permission_templates = permissions.account_templates
    permissions = models.CharField(max_length = 32)
    
    class Meta:
        app_label = 'twistranet'

    def save(self, apply_permissions = True, *args, **kw):
        """
        Populate special content information before saving it.
        XXX TODO: Check saving rights
        """
        # XXX TODO: Check security
        import _permissionmapping
        
        # Check account subtype
        if not self.account_type:
            if self.__class__.__name__ == Account.__name__:
                raise RuntimeError("You can't directly save an account object.")
            self.account_type = self.__class__.__name__
        
        # Call parent
        ret = super(Account, self).save(*args, **kw)
            
        # Set/reset permissions. We do it last to ensure we have an id. Ignore AttributeError from object.
        try:
            target = self.object
        except AttributeError:
            return ret
        _permissionmapping._applyPermissionsTemplate(target, _permissionmapping._AccountPermissionMapping)
        return ret

    @property
    def fullname(self,):
        """
        XXX TODO: user object.username?
        """
        if self.account_type == "UserAccount":
            return self.useraccount.user.username
        else:
            return self.id
        
    @property
    def object(self):
        """
        Return the actual object type.
        XXX Should be more efficient and/or more error-proof?
        """
        if self.id is None:
            raise RuntimeError("You can't get subclass until your object is saved in database.")
        return AccountRegistry.getModelClass(self.account_type).objects.get(id = self.id)
    
    def __unicode__(self):
        return u"%s" % (self.fullname, )
        
    @property
    def is_admin(self):
        """
        Return True if current user is in the admin community or is System
        """
        if self.account_type == "SystemAccount":
            return True
        # XXX TODO: Check admin community membership
        return False

    # Relations management
    @property
    def my_relations(self):
        """
        Return people I declared an interest for
        """
        return Account.objects.filter(target_whose__initiator = self)

    def getMyFollowed(self):
        """
        Return list of followed persons (ie. approval not set)
        """
        return Account.objects.filter(target_whose__initiator = self, target_whose__approved = False)
        
    def getMyFollowers(self):
        """
        Return list of people who follow me (ie. I didn't approve)
        """
        return Account.objects.filter(initiator_whose__target = self, initiator_whose__approved = False)

    @property
    def network(self):
        return self.getMyNetwork()

    def getMyNetwork(self):
        """
        Return list of my networked (ie. approved) people
        """
        # Both calls must return the same (normally...)
        return Account.objects.filter(initiator_whose__target = self, initiator_whose__approved = True)
        return Account.objects.filter(target_whose__initiator = self, target_whose__approved = True)
   
    @property
    def content(self):
        """
        return content visible by this account
        """
        from content import Content
        return Content.objects
        
    @property
    def communities(self):
        """
        Return communities this user is a member of
        """
        from community import Community
        return Community.objects.filter(members = self).distinct()
        
        
class SystemAccount(Account):
    """
    The system accounts for TwistraNet.
    There must be at least 1 system account called '_system'. It's its role to build initial content.
    System accounts can reach ALL content from ALL communities.
    """
    objects = AccountManager()
    
    class Meta:
        app_label = "twistranet"
        
    @staticmethod
    def getSystemAccount():
        """Return main (and only) system account"""
        return SystemAccount.objects.get()
AccountRegistry.register(SystemAccount)
        
class UserAccount(Account):
    """
    Generic User account.
    This holds user profile as well!
    """
    user = models.OneToOneField(User, unique=True, related_name = "useraccount")

    def __unicode__(self):
        return self.useraccount.user.username

    class Meta:
        app_label = 'twistranet'
AccountRegistry.register(UserAccount)

