from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from account import Account

COMMUNITY_SCOPES = (
    ("members", "Private community visible by its members only", ),
    ("authenticated", "A regular intranet community visible by logged-in users", ),
    ("anonymous", "Public community visible by anonymous users", ),
    )

class CommunityManager(models.Manager):
    """
    Useful shortcuts for community management.
    The manager itself only return 100% public communities when secured
    """
    def __init__(self, secured = True, *args, **kw):
        self._secured = secured
        super(CommunityManager, self).__init__(*args, **kw)
            
    def get_query_set(self):
        """
        Return either public or restricted communities
        """
        qs = super(CommunityManager, self).get_query_set()
        if self._secured:
            qs = qs.filter(scope = "anonymous")
        return qs
        

class Community(models.Model):
    """
    A simple community class.
    """
    # Managers overloading
    objects = CommunityManager(secured = True)
    _objects = CommunityManager(secured = False)
    
    # Usual metadata
    date = models.DateTimeField(auto_now = True)
    community_type = models.CharField(max_length = 64)
    name = models.TextField()
    description = models.TextField()
    
    # Members & security management
    members = models.ManyToManyField(Account, through = "CommunityMembership")
    # XXX user_source = (OPTIONAL)
    # XXX scope = ...
    scope = models.CharField(max_length=16, choices=COMMUNITY_SCOPES, blank = False, null = False)

    def __unicode__(self):
        return "%s %d: %s" % (self.community_type, self.id, self.name)
    
    class Meta:
        app_label = 'twistranet'
        
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        if self.scope not in [ t[0] for t in COMMUNITY_SCOPES ]:
            raise ValidationError("Invalid community scope: '%s'" % self.scope)
        # if self.community_type == Community.__name__:
        #     raise ValidationError("You cannot save a community object. Use a derived class instead.")
        self.community_type = self.__class__.__name__
        super(Community, self).save(self, *args, **kw)

    def _can_see(self, account):
        """
        Check if given account has access to this community. Raises if not.
        """
        from communitywrapper import CommunityWrapper
        wrapper = CommunityWrapper(account)
        wrapper.get(id = self.id)   # Will raise if unauthorized
    
    def join(self, account):
        """
        Join the community.
        You can only join the communities you can 'see'
        """
        # Quick security check
        self._can_see(account)
        
        # Don't add twice
        if self in wrapper.my:
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
        """
        # Quick security check, then delete membership info
        self._can_see(account)
        for mbr in CommunityMembership.objects.filter(account = account, community = self):
            mbr.delete()


class CommunityMembership(models.Model):
    """
    Community Membership association class.
    This is a many to many asso class
    """
    account = models.ForeignKey(Account)
    community = models.ForeignKey(Community)
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

    



