from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied

from account import Account, AccountManager
from accountregistry import AccountRegistry
import basemanager
from twistranet.lib import permissions

class CommunityManager(AccountManager):
    """
    Useful shortcuts for community management.
    The manager itself only return 100% public communities when secured
    """

    @property
    def global_(self):
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
    name = models.TextField()
    description = models.TextField()
    
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
        return super(Community, self).save(*args, **kw)
        
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
        account = Community.objects._getAuthenticatedAccount()
        return not not CommunityMembership.objects.filter(
            account = account, 
            community = self,
            is_invitation_pending = False,
            )

    def join(self, account = None):
        """
        Join the community.
        If account is None, assume it current authenticated account.
        You can only join the communities you can 'see'
        """
        # Check if current account is allowed to force another account to join
        current = Community.objects._getAuthenticatedAccount()
        if account:
            # Try to force joining sbdy? Check if we're allowed to.
            if not current.is_admin:
                raise PermissionDenied("You can't force a user to join a community.")
        else:
            account = current
        
        # Don't add twice
        # if account in self.members.filter(is_invitation_pending = False):
        #     return
        
        # Check join rules
        # XXX TODO: Actually check 'em!
        allowed = False
        if current.is_admin:
            allowed = True
        # else:
        #     # Handle easy cases
        #     if self.join_rule == COMMUNITYJOIN_AUTHENTICATED:
        #         allowed = True
        #     elif self.join_rule == COMMUNITYJOIN_CLOSED:
        #         allowed = False
        #     else:
        #         # Invitations management
        #         invitation = self.members.filter(
        #             account = account,
        #             community = self,
        #             # is_invitation_pending = True
        #             ).all()
        #         if not invitation:
        #             allowed = False
        #         elif self.join_rule == COMMUNITYJOIN_INVITED_BY_MEMBER:
        #             if invitation.invitation_from in self.members.filter(is_invitation_pending = False).all():  # XXX YERK!
        #                 allowed = True
        #         elif self.join_rule == COMMUNITYJOIN_INVITED_BY_MANAGER:
        #             if invitation.invitation_from in self.members.filter(is_invitation_pending = False, is_admin = True).all(): # XXX UGLY!
        #                 allowed = True
        #         elif self.join_rule == COMMUNITYJOIN_INVITED_BY_ADMIN:
        #             if invitation_from.is_admin:
        #                 allowed = True
        #         else:
        #             raise NotImplementedError("Unexpected join rule: '%s'" % self.join_rule)
       
        if allowed:
            mbr = CommunityMembership(
                account = account,
                community = self,
                )
            mbr.save()
        else:
            raise PermissionDenied("You're not allowed to join this community")
        
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

    class Meta:
        app_label = 'twistranet'

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
        
AccountRegistry.register(GlobalCommunity)

class AdminCommunity(Community):
    """
    Community in which users gain admin rights.
    Admin right = can do admin stuff on any community the user can see.
    """
    class Meta:
        app_label = 'twistranet'
        
    
        
AccountRegistry.register(AdminCommunity)

    



