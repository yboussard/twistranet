from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from account import Account
import basemanager
from scope import *

class CommunityManager(basemanager.BaseManager):
    """
    Useful shortcuts for community management.
    The manager itself only return 100% public communities when secured
    """
    def get_query_set(self):
        """
        Return a queryset of 100%-authorized objects.
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
        return base_query_set.filter(
            (
                # Public accounts
                Q(scope = ACCOUNTSCOPE_ANONYMOUS)
                ) | (
                # Auth-only communities
                Q(scope = ACCOUNTSCOPE_AUTHENTICATED)
                ) | (
                # Communities the bound user is a member of
                Q(members = authenticated, scope = ACCOUNTSCOPE_MEMBERS)
                )
            ).distinct()
        
    
    @property
    def global_(self):
        """
        Return the global community. May raise if no access right.
        """
        return self.get(community_type = "GlobalCommunity")

    @property
    def admin(self):
        """
        Return the admin community / communities
        """
        return self.filter(community_type = "AdminCommunity")


class Community(Account):
    """
    A simple community class.
    A community is an account which have members. Members are User accounts.
    """
    # Managers overloading
    objects = CommunityManager()
    
    # Usual metadata
    date = models.DateTimeField(auto_now = True)
    community_type = models.CharField(max_length = 64)
    name = models.TextField()
    description = models.TextField()
    
    # Members & security management
    members = models.ManyToManyField(Account, through = "CommunityMembership", related_name = "membership")
    # XXX user_source = (OPTIONAL)
    # XXX scope = ...

    def __unicode__(self):
        return "%s %d: %s" % (self.community_type, self.id, self.name)
    
    class Meta:
        app_label = 'twistranet'
        
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        if self.scope not in COMMUNITY_SCOPE_IDS:
            raise ValidationError("Invalid community scope: '%s'" % self.scope)
        self.community_type = self.__class__.__name__
        return super(Community, self).save(*args, **kw)

    def join(self, account = None):
        """
        Join the community.
        If account is None, assume it current authenticated account.
        You can only join the communities you can 'see'
        """
        # Get account and check security
        if not account:
            account = Community.objects._getAuthenticatedAccount()
            # XXX TODO: Check if __account__ has the right to add a member in the community!
        
        # Don't add twice
        if self in account.communities:
            return
        mbr = CommunityMembership(
            account = account,
            community = self,
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


class CommunityMembership(models.Model):
    """
    Community Membership association class.
    This is a many to many asso class
    """
    account = models.ForeignKey(Account)
    community = models.ForeignKey(Community, related_name = "membership_manager")
    date_joined = models.DateField(auto_now_add = True)

    class Meta:
        app_label = 'twistranet'

class GlobalCommunity(Community):
    """
    THE global community.
    """
    class Meta:
        app_label = 'twistranet'

class AdminCommunity(Community):
    """
    Community in which users gain admin rights.
    Admin right = can do admin stuff on any community the user can see.
    """
    class Meta:
        app_label = 'twistranet'

    



