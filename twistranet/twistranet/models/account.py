from django.db import models
from django.db.models import Q
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation
from django.conf import settings

import twistable
from resource import Resource
from twistranet.twistranet.lib import permissions, roles, languages, slugify
from twistranet.twistranet.signals import request_add_to_network, accept_in_network
from  twistranet.twistranet.lib.log import log

from fields import ResourceField

# Create your models here.
class Account(twistable.Twistable):
    """
    A generic account.
    This is an abstract class.
    Can be subclassed as a user account, group account, app account, etc
    """
    # Picture management.
    default_picture_resource_slug = "default_account_picture"
    
    # Security models available for the user
    # XXX TODO: Use a foreign key instead with some clever checking? Or a specific PermissionField?
    # XXX because there's a problem here as choices cannot be re-defined for subclasses.
    permission_templates = permissions.account_templates
    is_anonymous = False    # User shouldn't be anonymous
    
    # View overriding support
    type_summary_view = "account/summary.part.html"
    is_account = True
    
    _role_cache = {}
    
    @property
    def media_resource_manager(self,):
        """
        Return or create the media res manager for this account.
        XXX TODO: Security checks
        """
        from resourcemanager import FileSystemResourceManager
        if not self.can_edit:
            raise NotImplementedError("Shouldn't allow to access this if we can't edit")

        # Create one if necessary
        try:
            return self._media_resource_manager
        except ObjectDoesNotExist:
            fsrm = FileSystemResourceManager(account = self)
            fsrm.save()
            self._media_resource_manager = fsrm
            self.save()
        
        # Return it
        return self._media_resource_manager
    
    class Meta:
        app_label = 'twistranet'

    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        # Don't allow direct saving here
        if self.__class__ == Account:
            raise ValueError("You're not allowed to save an Account object. Save the derived object instead")
        
        # Validate title / slug
        if not self.title:
            if not self.slug:
                raise ValidationError("You must provide either a slug or a title for an account")
            self.title = self.slug
        elif not self.slug:
            self.slug = slugify.slugify(self.title)
            
        # Call parent and do post-save stuff
        return super(Account, self).save(*args, **kw)


    #                                                       #
    #               Rights / Security management            #
    #                                                       #

    def has_role(self, role, obj = None, ):
        """
        Return if SELF account has the given role on the given object.
        XXX TODO Heavily uses caching and optimize queries
        XXX TODO Make only one query for db-dependant roles?
        
        Warning: This method can return different results when called
        from the authenticated user or not. We should only cache calls made
        from currently authenticated user.
        
        If a user has a role on an object, that doesn't means he has a permision...
        
        You can pass either an obj or a twistable id (to avoid dereferencing the
        underlying object if we can, for performance reasons).
        
        XXX TODO: Oh, BTW, we should check if the role actually exists!
        """
        auth = self
        if obj is None:
            obj = self
                
        # System Account is allowed to do anything.
        if isinstance(auth, SystemAccount):
            return True
        if role == roles.system:
            return False
        
        # Owner has all roles lower than owner.
        nwk = auth.network_ids
        if (obj.id == auth.id) or (obj.owner_id == auth.id):
            if role <= roles.owner:
                return True
        elif role == roles.owner:
            return False
            
        # If we can access it, that means we have the public role.
        # But maybe it's worth checking?
        if role == roles.public:
            # XXX TODO: Double check here...
            return True

        # If is a manager, validate all roles < mgr
        if role <= roles.manager:
            if self.is_admin:
                return True
            elif role == roles.manager:
                return False
        
        # If in the object's network, validate that. Dereference only if needed.
        if issubclass(obj.model_class, Account):
            pub = obj.id
        else:
            # XXX Maybe we could avoid this unncessary query, though I doubt so
            pub = obj.publisher_id
        if pub in nwk:
            if role <= roles.network:
                return True
        elif role == roles.network:
            return False
                
        # We shouldn't reach there
        raise RuntimeError("Unexpected role (%s) asked for object '%s' (%s)" % (role, obj and obj.__class__.__name__, obj and obj.id))


    def has_permission(self, permission, obj):
        """
        Return true if authenticated user has been granted the given permission on obj.
        """
        # Check roles, strongest first to optimize caching.
        try:
            p_template = obj.model_class.permission_templates.get(obj.permissions)
        except KeyError:
            # XXX Perm template is invalid or incomplete... Should do something here...
            # But if we're on the system account, let's pass
            if issubclass(self.model_class, SystemAccount):
                return True
        if self.has_role(p_template[permission], obj):
            return True
        
        # Didn't find, we disallow
        return False

    @property
    def is_admin(self):
        """
        Return True if current user is in the admin community or is System.
        We cache this value.
        """
        v = getattr(self, '_is_admin', None)
        if v is not None:
            return v
        import community
        try:
            self._is_admin = community.AdminCommunity.objects.__booster__.get().is_member
        except community.AdminCommunity.DoesNotExist:
            # No admin community? Strange but possible at boostrap-time.
            self._is_admin = False
        return self._is_admin


    #                                           #
    #           Relations management            #
    #                                           #

    @property
    def network(self):
        """
        Return this user's network, that is UserAccount with only APPROVED relations.
        """
        return UserAccount.objects.filter(
            targeted_network__target__id = self.id,
            requesting_network__client__id = self.id,
        ).exclude(id = self.id)
        
    @property
    def network_ids(self,):
        """
        Return networks available for queries AAAND myself.
        XXX TODO: Cache this!
        """
        if hasattr(self, "_c_network_ids"):
            return self._c_network_ids
        
        ids = Account.objects.__booster__.filter(
            Q(targeted_network__target__id = self.id) | Q(id = self.id)
            ).values_list("id", flat = True)
        self._c_network_ids = ids
        return ids

    @property
    def content(self):
        """
        return content visible by this account
        """
        from content import Content
        return Content.objects.get_query_set()
        
    @property
    def followed_content(self):
        """
        Return followed content for this account
        """
        from content import Content
        return Content.objects.filter(
            Content.objects.get_follow_filter(self),
        ).distinct()
        
    @property
    def communities(self):
        """
        Return communities this user is actually a member of.
        """
        from community import Community
        return Community.objects.filter(
            targeted_network__target__id = self.id,
            requesting_network__client__id = self.id,
        )

    @property
    def communities_for_display(self,):
        """
        Used to display network information. Heavily cached and cleverly sorted.
        """
        return self.communities.order_by("-id")[:settings.TWISTRANET_NETWORK_IN_BOXES]

    @property
    def managed_communities(self):
        """The communities I'm a manager of"""
        return self.communities.filter(targeted_network__is_manager = True)   

class SystemAccount(Account):
    """
    The system accounts for TwistraNet.
    There must be at least 1 system account called '_system'. It's its role to build initial content.
    System accounts can reach ALL content from ALL communities.
    """
    default_picture_resource_slug = "default_systemaccount_picture"
    SYSTEMACCOUNT_ID = 1       # Global SystemAccount id. Should always be 1 as it's the first account created in the fixture.
    
    class Meta:
        app_label = "twistranet"
        
    @staticmethod
    def get():
        """Return main (and only) system account. Will raise if several are set."""
        return SystemAccount.objects.get()
        
        
class UserAccount(Account):
    """
    Generic User account.
    This holds user profile as well!.
    
    A user account has languages defined so that it primarily 'sees' his favorite languages.
    """
    user = models.OneToOneField(User, unique=True, related_name = "useraccount")
    is_anonymous = False

    # Actual user shortcuts.
    @property
    def email(self,):
        return self.user.email
    @property
    def first_name(self):
        return self.user.first_name
    @property
    def last_name(self):
        return self.user.last_name

    class Meta:
        app_label = 'twistranet'

    def save(self, *args, **kw):
        """
        Set the 'name' attibute from User Source.
        We don't bother checking the security here, the parent will do it.
        If this is a creation, ensure we join the GlobalCommunity as well.
        """
        from twistranet.twistranet.models import community
        if not self.slug:
            self.slug = self.user.username
        creation = not self.id
        ret = super(UserAccount, self).save(*args, **kw)

        # Join the global community. For security reasons, it's SystemAccount who does this.
        # Add myself to my own community as well.
        # XXX Maybe this has to be done BEFORE calling super() ?
        if creation:
            glob = community.GlobalCommunity.objects.get()
            __account__ = SystemAccount.objects.get()
            glob.join(self)
            self.follow(self)
            del __account__
            
        log.debug("Saved %s (title = %s)" % (self, self.title, ))
        return ret
        
    def getDefaultOwner(self,):
        return SystemAccount.get()
        
    def getDefaultPublisher(self,):
        from twistranet.twistranet.models import GlobalCommunity
        return GlobalCommunity.objects.get()

    #                                                                                       #
    #                                   Network management                                  #
    #                                                                                       #

    @property
    def network_for_display(self,):
        """
        Used to display network information. Heavily cached and cleverly sorted.
        """
        return self.network.order_by("-id")[:settings.TWISTRANET_FRIENDS_IN_BOXES]

    def add_to_my_network(self):
        """
        Ask currently auth account to follow this one.
        """
        from twistranet.twistranet.models.network import Network

        # If relation already exists, we silently pass
        auth = Account.objects._getAuthenticatedAccount()
        if self.id == auth.id:
            return
        you_to_me = Network.objects.filter(client = auth, target = self)
        if you_to_me.exists():
            return
            
        # Add the relation itself
        Network.objects.create(client = auth, target = self)
        
        # Then send the proper signal according to the symetry
        if Network.objects.filter(client = self, target = auth).exists():
            accept_in_network.send(
                sender = self.__class__,
                client = auth,
                target = self,
            )
        else:
            request_add_to_network.send(
                sender = self.__class__,
                client = auth,
                target = self,
            )
        
    def remove_from_my_network(self):
        """
        Ask the currently auth account to unfollow this one.
        Silently pass is the relation didn't exist.
        Note that removing from the network breaks the TWO symetrical relations!
        """
        from twistranet.twistranet.models.network import Network

        # If relation already exists, we silently pass
        auth = Account.objects._getAuthenticatedAccount()
        if self.id == auth.id:
            return
        Network.objects.filter(client = auth, target = self).delete()        
        Network.objects.filter(client = self, target = auth).delete()        

    @property
    def can_add_to_my_network(self,):
        """
        True if currently auth user can add the given one to its network.
        False if already in my network ;)
        """
        from twistranet.twistranet.models.network import Network
        if not self.can_list:
            return False
        auth = Account.objects._getAuthenticatedAccount()
        if auth.is_anonymous:
            return False
        if self.id == auth.id:
            return False
        return not Network.objects.filter(client = auth, target = self).exists()        
        
    @property
    def in_my_network(self):
        """
        True if current object is in auth's user nwk (or at least has a nwk confirmation pending)
        """
        from twistranet.twistranet.models.network import Network
        auth = Account.objects._getAuthenticatedAccount()
        if auth.is_anonymous:
            return False
        if self.id == auth.id:
            return False
        return Network.objects.filter(client = auth, target = self).exists()        
        
    @property
    def has_pending_network_request(self):
        """
        True if currently auth user has a request incoming for this very user
        """
        auth = Account.objects._getAuthenticatedAccount()
        if self.id == auth.id:
            return False
        if self.id in auth.network_ids:
            if auth.id in self.network_ids:
                return False        # Already approved
            return True             # Yet to be approved
        return False                # No request pending
        
    @property
    def has_received_network_request(self):
        """
        True if currently auth user has sent a request to this user
        """
        auth = Account.objects._getAuthenticatedAccount()
        if self.id == auth.id:
            return False
        if auth.id in self.network_ids:
            if self.id in auth.network_ids:
                return False        # Already approved
            return True             # Yet to be approved
        return False                # No request pending
        
        
    def get_pending_network_requests(self, returned_model = None):
        """
        List pending nwk user requests, ie. requests I yet have to approve.
        XXX MORE THAN SUBOPTIMAL !!!
        You can use the 'returned_model' parameter to restrict invitations to a specific model.
        Default is to return only UserAccount requests
        """
        if not returned_model:
            returned_model = UserAccount
        from twistranet.twistranet.models.network import Network
        requested_ids = Network.objects.filter(target = self).values_list("client__id", flat = True)
        accepted_ids = Network.objects.filter(client = self).values_list("target__id", flat = True)
        
        unvalidated_ids = []
        for i in requested_ids:
            if i in accepted_ids:
                continue
            unvalidated_ids.append(i)
            
        return returned_model.objects.filter(id__in = unvalidated_ids)
        

    # Follow / Unfollow support
    # Can be used in API but not in the web interface.

    def follow(self, account):
        """
        Ask current user to follow the other one
        """
        # XXX TODO: Check security
        from twistranet.twistranet.models.network import Network
        me_to_you = Network.objects.filter(client = self, target = account)
        if me_to_you.exists():
            return
        
        # Add the relation itself
        Network.objects.create(client = self, target = account)
        
    def unfollow(self, account):
        """
        XXX TODO: Check security
        """
        from twistranet.twistranet.models.network import Network
        Network.objects.filter(client = self, target = account).delete()        
        
    @property
    def followers(self,):
        """
        Return people following me
        XXX TODO: Cache this
        """
        return UserAccount.objects.filter(targeted_network__target__id = self.id)

    @property
    def following(self,):
        """
        Return ppl I follow
        XXX TODO: Cache this
        """
        return UserAccount.objects.filter(requesting_network__client__id = self.id)

class AnonymousAccount(UserAccount):
    """
    Representation of an anonymous account.
    Never instanciate that directly, the _getAuthenticatedAccount() takes care for you.

    Note that there is an AnonymousAccount table in DB, unfortunately :(
    """
    id = None
    is_admin = False
    is_anonymous = True

    class Meta:
        app_label = "twistranet"
        managed = False

    def save(self, *args, **kw):
        """
        Prohibit object saving.
        """
        raise RuntimeError("You're not allowed to save or edit the anonymous account.")
    
# Register handler for User creation.
# Each time a User object is created in DB, we create its profile here.
from django.db.models.signals import post_save
def create_profile(sender, instance, created, *args, **kw):
    """
    Create an empty profile for a new user.
    XXX TODO: Handle particular LDAP attributes? 
    See http://packages.python.org/django-auth-ldap/#user-objects for more info
    """
    if created:
        # Here we check if AdminCommunity exists.
        # If it doesn't, that probably means we're inside the bootstrap process,
        # and in such case we don't want to create a profile now.
        import community
        if not community.AdminCommunity.objects.__booster__.exists():
            log.debug("Admin community doesn't exist (yet)")
            return
            
        # We consider we're the SystemAccount now.
        __account__ = SystemAccount.get()
        
        # Actually create profile
        log.info("Automatic creation of a UserAccount for %s" % instance)
        profile = UserAccount(
            user = instance,
            slug = slugify.slugify(instance.username),
        )
        profile.save()
    
post_save.connect(create_profile, sender = User)
        

class AccountLanguage(models.Model):
    """
    An intermediate model class to handle user -> languages problem.
    This is not a reference table.
    """
    order = models.IntegerField()
    language = models.CharField(
        max_length = 10,
        blank = True,
        choices = languages.available_languages,
        default = languages.available_languages[0][0],
        )
    account = models.ForeignKey(UserAccount, related_name = "account_languages")

    class Meta:
        app_label = 'twistranet'

    def __unicode__(self):
        return self.language

        

