from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied

from account import Account
from accountregistry import AccountRegistry
import basemanager
from twistranet.lib import permissions

class CommunityManager(basemanager.BaseManager):
    """
    Useful shortcuts for community management.
    The manager itself only return 100% public communities when secured
    """
    def get_query_set(self):
        """
        Return a queryset of 100%-authorized (in view) objects.
        """
        # Check for anonymous query
        authenticated = self._getAuthenticatedAccount()
        base_query_set = super(CommunityManager, self).get_query_set()
        if not authenticated:
            # TODO: Return anonymous objects
            raise NotImplementedError("TODO: Implement anonymous queries")

        # System account: return all objects
        if authenticated.account_type == "SystemAccount":
            authenticated.systemaccount   # This is one more security check, will raise if DB is not properly set
            return base_query_set  # The base qset with no filter

        # Account filter
        # XXX TODO: filter communities!
        return base_query_set.distinct()
            # (
            #     # Public accounts
            #     Q(scope = ACCOUNTSCOPE_ANONYMOUS)
            #     ) | (
            #     # Auth-only communities
            #     Q(scope = ACCOUNTSCOPE_AUTHENTICATED)
            #     ) | (
            #     # Communities the bound user is a member of
            #     Q(members = authenticated, scope = ACCOUNTSCOPE_MEMBERS)
            #     )
            # ).distinct()
    
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


class Community(Account):
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
    # initial_template = models.CharField(max_length = 32)
    # join_rule = models.IntegerField(choices = COMMUNITY_JOIN_RULES_IDS)
    # publish_rule = models.IntegerField(choices = COMMUNITY_PUBLISH_RULES_IDS)
    # scope = models.IntegerField(choices = COMMUNITY_SCOPES)   # XXX TODO: Restrict to community scopes only!
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
    """
    class Meta:
        app_label = 'twistranet'
AccountRegistry.register(GlobalCommunity)

class AdminCommunity(Community):
    """
    Community in which users gain admin rights.
    Admin right = can do admin stuff on any community the user can see.
    """
    class Meta:
        app_label = 'twistranet'
AccountRegistry.register(AdminCommunity)

    



