from django.db import models, IntegrityError
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.urlresolvers import NoReverseMatch
from account import Account, UserAccount, SystemAccount
from network import Network
from twistable import Twistable
from twistranet.lib import permissions, roles, notifier

class Community(Account):
    """
    A simple community class.
    A community is an account which have members. Members are User accounts.
    """
    # Usual metadata
    date = models.DateTimeField(auto_now = True)
    default_picture_resource_slug = "default_community_picture"
    
    # Members & security management
    # members = models.ManyToManyField(Account, through = "CommunityMembership", related_name = "membership")
    # XXX user_source = (OPTIONAL)
    permission_templates = permissions.community_templates

    # View overriding support
    # XXX TODO: Find a way to optimize this without having to query the underlying object
    summary_view = "community/summary.part.html"
    is_community = True
    
    @property
    def managers(self):
        return self.members.filter(targeted_network__is_manager = True).distinct()
        
    @property
    def members(self):
        return Account.objects.filter(
            targeted_network__target__id = self.id,
            requesting_network__client__id = self.id,
        )
        
    @property
    def members_for_display(self):
        """
        Same as members but we really know we're going to display related information on them.
        XXX TODO Use related() to optimize things here
        """
        return self.members
        
    @property
    def managers_for_display(self):
        """Same as members_for_display but for managers"""
        return self.managers

    class Meta:
        app_label = 'twistranet'
        
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        ret = super(Community, self).save(*args, **kw)
        if not self.is_member:
            auth = Twistable.objects._getAuthenticatedAccount()
            if not isinstance(auth, SystemAccount):
                Network.objects.create(
                    client = auth,
                    target = self,
                    is_manager = True,
                )
                Network.objects.create(
                    client = self,
                    target = auth,
                    is_manager = False,
                )
        return ret
        
    def delete(self, ):
        """
        Check the can_delete permission before dumping content.
        XXX Todo: delete nwk as well
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
        XXX HAVE TO OPTIMIZE (PRE-LOAD?) THIS!
        """
        if not account:
            account = Community.objects._getAuthenticatedAccount()
            if not account:
                return False    # Anon user
        flt = Account.objects.__booster__.filter(
            targeted_network__target__id = self.id,
            targeted_network__client__id = account.id,
            requesting_network__client__id = self.id,
            requesting_network__target__id = account.id,
        )

        if is_manager:
            flt = flt.filter(
                targeted_network__is_manager = True,
            )

        return flt.exists()

            
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
        return self.join(account, is_manager = True)
                
    @property
    def can_join(self):
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_join, self)
        
    @property
    def can_leave(self):
        # Special check if we're not the last (human) manager inside
        if self.is_manager:
            if self.managers.count() == 1:
                return False
        
        # Regular checks
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_leave, self)
            
    def join(self, account = None, is_manager = False):
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

        # Actually add (symetrically).
        # We ignore Integrity Errors as they are just duplicate of the same information
        try:
            Network.objects.create(
                client = account,
                target = self,
                is_manager = is_manager,
            )
        except IntegrityError:
            pass
        try:
            Network.objects.create(
                client = self,
                target = account,
                is_manager = False,
            )
        except IntegrityError:
            pass
        
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
        
        Network.objects.__booster__.filter(client__id = self.id, target__id = account.id).delete()
        Network.objects.__booster__.filter(target__id = self.id, client__id = account.id).delete()


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




