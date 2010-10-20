from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied

from account import Account, AccountManager, UserAccount, SystemAccount
from accountregistry import AccountRegistry
import basemanager
from twistranet.lib import permissions, roles

class CommunityManager(AccountManager):
    """
    Useful shortcuts for community management.
    The manager itself only return 100% public communities when secured
    """
    @property
    def global_(self,):
        """
        Return the global community. May raise if no access right.
        """
        return self.get(account_type = "GlobalCommunity")

    @property
    def admin(self):
        """
        Return the admin community / communities
        """
        return self.filter(account_type = "AdminCommunity")

class _AbstractCommunity(Account):
    """
    We use this to enforce using our manager on subclasses.
    This way, we avoid enforcing you to re-declare objects = AccountManager() on each account class!

    See: http://docs.djangoproject.com/en/1.2/topics/db/managers/#custom-managers-and-model-inheritance
    """
    class Meta:
        abstract = True

    # Our security model
    objects = CommunityManager()


class Community(_AbstractCommunity):
    """
    A simple community class.
    A community is an account which have members. Members are User accounts.
    """
    # Managers overloading
    objects = CommunityManager()
    
    # Usual metadata
    date = models.DateTimeField(auto_now = True)
    default_picture_resource_alias = "default_community_picture"
    
    # Members & security management
    members = models.ManyToManyField(Account, through = "CommunityMembership", related_name = "membership")
    # XXX user_source = (OPTIONAL)
    permission_templates = permissions.community_templates

    class Meta:
        app_label = 'twistranet'
        
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        auth = Community.objects._getAuthenticatedAccount()
        ret = super(Community, self).save(*args, **kw)
        if isinstance(auth.object, UserAccount) and not self.isMember(auth):
            CommunityMembership.objects.create(
                account = auth,
                community = self,
                is_manager = True,
            )
        return ret
        
    def setTemplate(self, template_id):
        """
        Reset community attributes to match those of the specified template.
        Changing the initial_template value has no effect.
        """
        raise NotImplementedError("Have to implement this")

    @property
    def is_member(self):
        """
        Return true if currently auth user is a member of the community
        """
        return self.isMember()
            
    def isMember(self, account = None, is_manager = False):
        """
        Return True if given account is member.
        If account is None, assume it's current authenticated.
        """
        if not account:
            account = Community.objects._getAuthenticatedAccount()
            if not account:
                return False    # Anon user
                
        qs = CommunityMembership.objects.filter(
            account = account, 
            community = self,    
            )
        if is_manager:
            qs = qs.filter(is_manager = True)
        return qs.exists()

            
    @property
    def is_manager(self):
        """
        Return true if current user is a community manager
        """
        return self.isMember(is_manager = True)

    def join_manager(self, account = None):
        """
        Same as join() but as a manager.
        Only a community manager (or the first community member) can do that.
        """
        return self.join(account, manager = True)
        
    @property
    def can_join(self):
        return self.canJoin()
        
    def canJoin(self, account = None, manager = False):
        """
        Return True if given user can join.
        Will return False if already a member.
        """
        # Get account
        authenticated = Community.objects._getAuthenticatedAccount()
        if not account:
            account = authenticated
            
        # If he're already in it, just pass
        if self.members.filter(id = account.id).exists():
            return False
        
        # Is current user is admin? If so, he can join anything
        if account.is_admin or authenticated.is_admin:
            return True

        # Allowed anonymous join? Hum, that's strange
        if roles.anonymous.allowed_by(self._permissions):
            raise ValidationError("Anonymous shouldn't be able to join %s community." % self)    

        # If auth users are authorized, then go (provided account logged).
        elif roles.authenticated.allowed_by(self._permissions):
            if not manager:
                return not not account
            
        # Invalid role
        elif roles.account_network.allowed_by(self._permissions):
            raise ValidationError("Unexpected can_join role %s" % (self, ))
            
        elif roles.community_member.allowed_by(self._permissions):
            if manager:
                return False
            if self.is_member:
                return True
                
        # From here, we allow manager adds
        elif roles.community_manager.allowed_by(self._permissions):
            if self.is_manager:
                return True
        elif roles.administrator.allowed_by(self._permissions):
            if authenticated.is_admin:
                return True
        elif roles.system.allowed_by(self._permissions):
            if isinstance(authenticated, SystemAccount):
                return True
        else:
            raise ValidationError("Unexpected can_join role %s" % (self, ))
        
        # No match? So bad.
        return False
        
    def join(self, account = None, manager = False):
        """
        Join the community.
        If account is None, assume it current authenticated account.
        You can only join the communities you can 'see'
        """
        # Check if current account is allowed to force another account to join
        if not self.canJoin(account, manager):
            raise PermissionDenied("You can't force a user to join a community.")

        # Actually add
        mbr = CommunityMembership(
            account = account,
            community = self,
            is_manager = manager,
            )
        mbr.save()
        
    def leave(self, account):
        """
        Leave the community.
        Fails silently is account is not a member of the community.
        XXX TODO: Check security
        """
        # Quick security check, then delete membership info
        for mbr in CommunityMembership.objects.filter(account = account, community = self):
            mbr.delete()

# XXX TODO: Use a class decorator instead (if it ever exists?)
AccountRegistry.register(Community)

class CommunityMembership(models.Model):
    """
    Community Membership association class.
    This is a many to many asso class
    """
    account = models.ForeignKey(Account)
    community = models.ForeignKey(Community, related_name = "membership_manager")
    date_joined = models.DateField(auto_now_add = True)
    is_manager = models.BooleanField(default = False)               # True if community manager
    # is_invitation_pending = models.BooleanField(default = False)    # True if invited by sbd
    # invitation_from = models.ForeignKey(Account, related_name = "invite_to_community_membership")

    def __unicode__(self):
        if self.is_manager:
            return "%s is a community manager for %s" % (self.account, self.community, )
        return "%s is member of %s" % (self.account, self.community, )

    class Meta:
        app_label = 'twistranet'
        unique_together = ('account', 'community')

class GlobalCommunity(Community):
    """
    THE global community.
    
    The global community also has all the webmaster-level settings of Twistranet.
    can_view must be given to either anonymous or authenticated role for TN to work!
    If can_view is authenticated, then ALL OF Twistranet is restricted to auth people.
    
    Default is authenticated.
    """
    class Meta:
        app_label = 'twistranet'
    permission_templates = permissions.global_community_templates

    @staticmethod
    def get():
        """Return main (and only) system account. Will raise if several are set."""
        return self.__class__.objects.get()
        
AccountRegistry.register(GlobalCommunity)

class AdminCommunity(Community):
    """
    Community in which users gain admin rights.
    Admin right = can do admin stuff on any community the user can see.
    """
    class Meta:
        app_label = 'twistranet'
        
    @staticmethod
    def get():
        """Return main (and only) system account. Will raise if several are set."""
        return self.__class__.objects.get()

        
AccountRegistry.register(AdminCommunity)

    



