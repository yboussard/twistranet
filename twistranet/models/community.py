from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied

from account import Account, AccountManager, UserAccount, SystemAccount
import basemanager
from twistranet.lib import permissions, roles, notifier, AccountRegistry

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
        return self.get(object_type = "GlobalCommunity")

    @property
    def admin(self):
        """
        Return the admin community / communities
        """
        return self.get(object_type = "AdminCommunity")

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
    # Usual metadata
    date = models.DateTimeField(auto_now = True)
    default_picture_resource_slug = "default_community_picture"
    
    # Members & security management
    members = models.ManyToManyField(Account, through = "CommunityMembership", related_name = "membership")
    # XXX user_source = (OPTIONAL)
    permission_templates = permissions.community_templates

    # View overriding support
    # XXX TODO: Find a way to optimize this without having to query the underlying object
    summary_view = "community/summary.part.html"
    is_community = True
    
    @property
    def managers(self):
        return CommunityMembership.objects.filter(community = self, is_manager = True)

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
        
    def delete(self, ):
        """
        Check the can_delete permission before dumping content
        """
        if not self.can_delete:
            raise PermissionDenied("You're not allowed to delete this community")
        return super(Community, self).delete()
        
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
    def can_edit(self):
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_edit, self)
        
    @property
    def can_join(self):
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_join, self)
        
    @property
    def can_leave(self):
        # Special check if we're not the last manager inside
        if self.is_manager:
            if self.managers.count() == 1:
                return False
        
        # Regular checks
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_leave, self)
        
    @property
    def can_delete(self):
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_delete, self)
    
    def join(self, account = None, manager = False):
        """
        Join the community.
        If account is None, assume it current authenticated account.
        """
        # Check if current account is allowed to force another account to join
        if not self.can_join:
            if account:
                raise PermissionDenied("You're not allowed to let somebody join this community.")
            else:
                raise PermissionDenied("You're not allowed to join this community. You must be invited.")
        
        if not account:
            account = Account.objects._getAuthenticatedAccount()

        # Actually add
        mbr = CommunityMembership(
            account = account,
            community = self,
            is_manager = manager,
            )
        mbr.save()
        
        # Post join message
        notifier.joined(account, self)
        
    def leave(self, account):
        """
        Leave the community.
        Fails silently is account is not a member of the community.
        """
        if not self.can_leave:
            if account:
                raise PermissionDenied("You're not allowed to exclude somebody from this community.")
            else:
                raise PermissionDenied("You're not allowed to leave this community")
            
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
    
    This community holds all the TN configuration as well!
    """
    class Meta:
        app_label = 'twistranet'
    permission_templates = permissions.global_community_templates
    
    site_name = models.CharField(
        max_length = 64,
        help_text = "Enter this site's name. It will be displayed prominently on all pages. No HTML please.",
        default = "TwistraNet",
        )
    baseline = models.CharField(
        max_length = 64,
        help_text = "Enter the site's baseline. It will be displayed in the upper bar of the site. No HTML please.",
        default = "Enjoy working in team.",
        )

    @classmethod
    def get(cls):
        """Return main (and only) system account. Will raise if several are set."""
        return cls.objects.get()
        
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

    



