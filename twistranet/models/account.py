from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied

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
            # Return only anonymous objects and system accounts
            # Special shortcut to check if anonymous access is authorized
            # Unless we do this, we can have an infinite recursion!
            # XXX TODO: Improve this to avoid a possibly unncessary query; cache it?
            import _permissionmapping
            if _permissionmapping._AccountPermissionMapping._objects.filter(
                target__account_type = "GlobalCommunity",
                name = permissions.can_list,
                role = roles.anonymous,
                ).count():
                # Opened to anonymous. Return public stuff.
                return base_query_set.filter(
                    _permissions__name = permissions.can_list,
                    _permissions__role = roles.anonymous,
                    )
            else:
                # Just return the system account, as we must be able to bootstrap with it ?
                # XXX Maybe we should not even return that!
                return base_query_set.filter(account_type = "SystemAccount")

        # System account: return all objects
        if authenticated.account_type == "SystemAccount":
            authenticated.systemaccount     # This is one more security check, will raise if DB is not properly set
            return base_query_set           # The base qset with no filter

        # Regular Account filter, return only listed accounts.
        # For Account objects, we don't check members. For Community objects, we do ;)
        from community import Community
        if issubclass(self.model, Community):
            # Community objects can use the 'members' query parameter directly
            community_subquery = Q(members = authenticated)
        elif self.model == Account:
            # Regular Account objects must de-reference the community first
            community_subquery = Q(
                community__members = authenticated
                )
        else:
            # Account-derived objects that are not communities have no 'members' attribute.
            # But we need to check if user is in the network
            community_subquery = Q(
            )

        # Perform the filter
        return base_query_set.filter(
            Q(
                # Myself
                id = authenticated.id
            ) | Q(
                # Public accounts, ie. stuff any auth ppl can list
                _permissions__name = permissions.can_list,
                _permissions__role__in = roles.authenticated.implied(),
            ) | Q(
                # People in account's network
                _permissions__name = permissions.can_list,
                _permissions__role__in = roles.account_network.implied(),
                initiator_whose__target = authenticated,
            ) | community_subquery)

class _AbstractAccount(models.Model):
    """
    We use this to enforce using our manager on subclasses.
    This way, we avoid enforcing you to re-declare objects = AccountManager() on each account class!

    See: http://docs.djangoproject.com/en/1.2/topics/db/managers/#custom-managers-and-model-inheritance
    """
    can_view_fields = ('id', 'account_type', 'name', 'picture', 'user', )
    
    def __getattribute__(self, key):
        """
        Protect fields that have to be protected with the can_view permission but not the can_list permission.
        By default, ALL fields are protected against view except if they're explicitly mentionned 
        in the 'can_view_fields' pty of the class.
        """
        super_getattr = super(_AbstractAccount, self).__getattribute__
        if key in [ f.name for f in super_getattr("_meta").fields ]:
            if not key in super_getattr("__class__").can_view_fields:
                authenticated = basemanager._getAuthenticatedAccount()
                # No account => anonymous => buerck
                if not authenticated:
                    raise PermissionDenied("Unauthorized field access: %s" % key)
                elif isinstance(authenticated, SystemAccount):
                    # System account; we can go
                    pass
                else:
                    # If we're here, then we know we've been listed. Study the can_list permission carefuly.
                    account_roles = [ p.role for p in super_getattr("_permissions").filter(name = permissions.can_view) ]
                    
                    # Anonymous / Public can view, ok, we pass
                    if roles.anonymous.value in account_roles:
                        return super_getattr(key)
                    elif roles.authenticated.value in account_roles:
                        return super_getattr(key)
                    elif roles.account_network.value in account_roles:
                        if authenticated in super_getattr('network'):
                            return super_getattr(key)
                    elif roles.community_member.value in account_roles:
                        if super_getattr('members').filter(id = authenticated.id):
                            return super_getattr(key)
                    elif roles.community_manager.value in account_roles:
                        if authenticated in super_getattr('members'):
                            # XXX TODO: Check community managers, not just members
                            return super_getattr(key)
                    elif roles.administrator.value in account_roles:
                        # XXX TODO: Check if in admin community
                        pass
                    else:
                        raise ValueError("Unexpected roles for account %s: %s" % (self, account_roles))

                    # Can't find a match? So bad.
                    raise PermissionDenied("Unauthorized field access: %s" % key)
        return super_getattr(key)
    
    
    class Meta:
        abstract = True

    # Our security model
    objects = AccountManager()



# Create your models here.
class Account(_AbstractAccount):
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
    picture = models.ForeignKey("Resource", null = True)    # Ok, this is odd but it's because of the bootstrap.
                                                            # We'll avoid the 'null' attribute someday.
    objects = AccountManager()
    description = models.TextField()

    # Security models available for the user
    # XXX TODO: Use a foreign key instead with some clever checking? Or a specific PermissionField?
    # XXX because there's a problem here as choices cannot be re-defined for subclasses.
    permission_templates = permissions.account_templates
    permissions = models.CharField(max_length = 32)
    
    class Meta:
        app_label = 'twistranet'

    @property
    def permissions_list(self):
        import _permissionmapping
        return _permissionmapping._ContentPermissionMapping.objects._get_detail(self.id)

    def save(self, *args, **kw):
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
            
        # Set/reset permissions. We do it last to ensure we have an id. Ignore AttributeError from object pty
        _permissionmapping._AccountPermissionMapping.objects._applyPermissionsTemplate(
            self, _permissionmapping._AccountPermissionMapping
            )
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
    def model_class(self):
        """
        Return the subobject model class
        """
        return AccountRegistry.getModelClass(self.account_type)
        
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
        """Return main (and only) system account. Will raise if several are set."""
        return SystemAccount.objects.get()
        
    def __unicode__(self):
        return "SystemAccount (%d)" % self.id
        
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

