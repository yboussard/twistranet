from django.db import models
from django.db.models import Q
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation

import basemanager
import securable
from resource import Resource
from twistranet.lib import permissions, roles, languages, utils, AccountRegistry
from django.db.utils import DatabaseError

class AccountManager(basemanager.BaseManager):
    """
    This manager is used for secured account.
    """
    def get_query_set(self):
        """
        Return a queryset of 100%-authorized objects.
        We could use the can_list permission to check each individual object,
        but that'd be at the expense of speed.
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
            try:
                if _permissionmapping._AccountPermissionMapping._objects.filter(
                    target__object_type = "GlobalCommunity",
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
                    return base_query_set.filter(object_type = "SystemAccount")
            except DatabaseError:
                # Avoid bootstrap quircks. XXX VERY DANGEROUS, should limit that to table doesn't exist errors!
                return base_query_set.none()

        # System account: return all objects
        if authenticated.object_type == "SystemAccount":
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
        # XXX TODO: Avoid the distinct() method to optimize. The two last 'Q' methods are redundant.
        # I should use & ~Q(id = authenticated.id) and restrict the roles implied
        return base_query_set.filter(
            Q(
                # Myself
                id = authenticated.id
            ) | (
                Q(
                    # Public accounts, ie. stuff any auth ppl can list
                    _permissions__name = permissions.can_list,
                    _permissions__role__in = roles.authenticated.implied(),
                )
            ) | (
                Q(
                    # People in account's network
                    _permissions__name = permissions.can_list,
                    _permissions__role__in = roles.account_network.implied(),
                    initiator_whose__target = authenticated,
                )
            ) | community_subquery).distinct()

class _AbstractAccount(securable.Securable):
    """
    We use this to enforce using our manager on subclasses.
    This way, we avoid enforcing you to re-declare objects = AccountManager() on each account class!

    See: http://docs.djangoproject.com/en/1.2/topics/db/managers/#custom-managers-and-model-inheritance
    """
    # We keep the following code if we ever need to enforce more powerful security (at the expense of speed)    
    # can_view_fields = ('id', 'object_type', 'slug', 'picture', 'user', )
    # def __getattribute__(self, key):
    #     """
    #     Protect fields that have to be protected with the can_view permission but not the can_list permission.
    #     By default, ALL fields are protected against view except if they're explicitly mentionned 
    #     in the 'can_view_fields' pty of the class.
    #     """
    #     super_getattr = super(_AbstractAccount, self).__getattribute__
    #     if key in [ f.slug for f in super_getattr("_meta").fields ]:
    #         if not key in super_getattr("__class__").can_view_fields:
    #             if not super_getattr("can_view"):
    #                 raise PermissionDenied("Unauthorized field access: %s" % key)
    #     return super_getattr(key)
    
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
    screen_name = models.CharField(max_length = 64, db_index = True, null = False, blank = False)               # The screenname (ie. the 'pseudo' used to display the account name).
                                                                                                                # This may be translatable someday.
                                                                    
    # Picture management.
    # If None, will use the default_picture_resource_slug attribute.
    # If you want to get the account picture, use the 'picture' attribute.
    default_picture_resource_slug = "default_profile_picture"
    picture = models.ForeignKey("Resource")        # Ok, this is odd but it's because of the bootstrap.
                                                                # XXX We should avoid the 'null' attribute someday. Not easy 'cause of the SystemAccount bootstraping...
    objects = AccountManager()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now = True, db_index = True)

    # Security models available for the user
    # XXX TODO: Use a foreign key instead with some clever checking? Or a specific PermissionField?
    # XXX because there's a problem here as choices cannot be re-defined for subclasses.
    permission_templates = permissions.account_templates
    permissions = models.CharField(
        max_length = 32,
        db_index = True,
        )
    
    # View overriding support
    # XXX TODO: Find a way to optimize this without having to query the underlying object
    summary_view = "account/summary.part.html"
    is_account = True
    
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
        XXX TODO: Check saving rights
        """
        # XXX TODO: Check security
        import _permissionmapping
        
        # Check account subtype
        if not self.object_type:
            if self.__class__.__name__ == Account.__name__:
                raise RuntimeError("You can't directly save an account object. Use 'account.object.save()' method instead.")
            self.object_type = self.__class__.__name__
        
        # Validate screen_name / slug
        if not self.screen_name:
            if not self.slug:
                raise ValidationError("You must provide either a slug or a screen_name for an account")
            self.screen_name = self.slug
        elif not self.slug:
            self.slug = utils.slugify(self.screen_name)
            
        # Default permissions
        if not self.permissions:
            self.permissions = self.permission_templates.get_default()
            
        # Set default picture if not set
        if not self.picture_id and not self.object_type == 'SystemAccount':
            self.picture = Resource.objects.get(slug = self.default_picture_resource_slug)
            
        # Call parent
        ret = super(Account, self).save(*args, **kw)
            
        # Set/reset permissions. We do it last to ensure we have an id. Ignore AttributeError from object pty
        _permissionmapping._AccountPermissionMapping.objects._applyPermissionsTemplate(self)
        return ret
        
    @property
    def model_class(self):
        """
        Return the subobject model class
        """
        return AccountRegistry.getModelClass(self.object_type)
        
    @property
    def object(self):
        """
        Return the actual object type.
        XXX Should be more efficient and/or more error-proof?
        """
        if self.id is None:
            raise RuntimeError("You can't get subclass until your object is saved in database.")
            
        # Shortcuts for performance reasons
        if self.object_type == self.__class__.__name__:
            return self
        obj = getattr(self, self.object_type.lower(), None)
        if obj:
            return obj
        return AccountRegistry.getModelClass(self.object_type).objects.get(id = self.id)
    
    def __unicode__(self):
        return u"%s" % (self.screen_name, )

    #                                                       #
    #               Rights / Security management            #
    #                                                       #


    def has_role(self, role, obj = None):
        """
        Return if SELF account has the given role on the given object.
        XXX TODO Heavily uses caching and optimize queries
        XXX TODO Make only one query for db-dependant roles?
        Some roles are global (authenticated, anonymous, administrator, ..), 
        and some are dependent of the given object (community_member, ...).
        
        Warning: This method can return different results when called
        from the authenticated user or not. We should only cache calls made
        from currently authenticated user.
        
        If a user has a role on an object, that doesn't means he has a permision.
        
        XXX TODO: Oh, BTW, we should check if the role actually exists!
        """
        # Role computing
        if isinstance(role, roles.Role):
            role = role.value
            
        # Gory admin shortcuts
        if self.object_type == "SystemAccount":
            return True
            
        # Global roles.
        if role == roles.anonymous.value:
            return True             # An account always has the anonymous role
                                    # Should not be cached, BTW
        
        if role == roles.authenticated.value:
            return Account.objects._getAuthenticatedAccount() == self      # Don't cache that
        
        if role == roles.administrator.value:
            if self.object_type == "SystemAccount":
                return True
            elif self.my_communities.filter(object_type = "AdminCommunity"):
                return True
            else:
                return False
                
        if role == roles.system.value:
            return self.object_type == "SystemAccount"
    
        # Account-related roles
        if isinstance(obj, Account):
            if role == roles.account_network.value:
                return not not obj.network.filter(id = self.id)
            if role == roles.owner.value:
                return obj.id == self.id
        
            # Community-related roles
            if role == roles.community_member.value:
                return self.my_communities.filter(id = obj.id).exists()
            if role == roles.community_manager.value:
                return self.my_managed_communities.filter(id = obj.id).exists()
            
        # Content-related roles
        import content
        if isinstance(obj, content.Content):
            if role == roles.content_public.value:
                return self.has_permission(permissions.can_view, obj.publisher)
            if role == roles.content_network.value:
                return self.has_role(roles.network, obj.publisher)
            if role == roles.content_community_member.value:
                return self.has_role(roles.community_member, obj.publisher)
            if role == roles.content_community_manager.value:
                return self.has_role(roles.community_manager, obj.publisher)
            if role == roles.owner.value:
                return obj.author.id == self.id

        # We shouldn't reach there
        raise RuntimeError("Unexpected role (%d) asked for object '%s' (%d)") % (role, obj and obj.__class__.__name__, obj and obj.id)


    def has_permission(self, permission, obj):
        """
        Return true if authenticated user has been granted the given permission on obj.
        XXX TODO: Heavily optimize and use caching!
        """
        # Check roles, strongest first to optimize caching.
        p_template = obj.object.permission_templates.get(obj.permissions)
        for role in p_template[permission]:         # Will raise if permission is not set on the given content
            if self.has_role(role, obj):
                return True

        # # DB checking disabled for performance reasons
        # for perm in obj._permissions.filter(name = permission).order_by('-role'):
        #     if self.has_role(perm.role, obj):
        #         return True
        
        # Didn't find, we disallow
        return False

    @property
    def can_publish(self):
        """
        True if authenticated account can publish on the current account object
        """
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_publish, self)

    @property
    def can_list(self):
        """
        Return true if the current account can list the current object.
        """
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_list, self)

    @property
    def can_view(self):
        """
        Return true if the current account can view the current object.
        """
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_view, self)

    @property
    def can_edit(self):
        """
        Return true if the current account can view the current object.
        """
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_edit, self)

    @property
    def is_admin(self):
        """
        Return True if current user is in the admin community or is System
        """
        return self.has_role(roles.administrator)


    #                                           #
    #           Relations management            #
    #                                           #
    
    def follow(self, account):
        """
        Ask this account to follow another one.
        """
        # XXX TODO: CHECK SECURITY HERE!
        from twistranet.models.relation import Relation
        me_to_you = Relation.objects.filter(initiator = self, target = account)
        if me_to_you.exists():
            # Already exists
            return
        
        # If the given account already follows me, then we consider the relation as approved
        you_to_me = Relation.objects.filter(initiator = account, target = self)
        if you_to_me.exists():
            you_to_me = you_to_me.get()
            you_to_me.approved = True
            you_to_me.save()
            approved = True
        else:
            approved = False
        me_to_you = Relation(initiator = self, target = account, approved = approved)
        me_to_you.save()
    
    @property
    def my_relations(self):
        """
        Return people I declared an interest for
        """
        return Account.objects.filter(target_whose__initiator = self)
        
    @property
    def my_communities(self):
        """The communities I'm a member of"""
        from community import Community
        return Community.objects.filter(members = self).distinct()
        
    @property
    def my_managed_communities(self):
        """The communities I'm a manager of"""
        from community import Community
        return Community.objects.filter(
            membership_manager__is_manager = True,
            membership_manager__account = self,
            ).distinct()
            
    @property
    def my_interest(self):
        """
        Return a list of accounts I'm interested in.
        """
        return Account.objects.filter(Q(target_whose__initiator = self) | Q(community__members = self)).distinct()

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
        # FYI, both calls must return the same (normally...)
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
        return Community.objects.filter(members = self)
        
        
class SystemAccount(Account):
    """
    The system accounts for TwistraNet.
    There must be at least 1 system account called '_system'. It's its role to build initial content.
    System accounts can reach ALL content from ALL communities.
    """
    objects = AccountManager()
    default_picture_resource_slug = "default_system_picture"
    
    class Meta:
        app_label = "twistranet"
        
    @staticmethod
    def get():
        """Return main (and only) system account. Will raise if several are set."""
        return SystemAccount.objects.get()
        
    def __unicode__(self):
        return "SystemAccount (%d)" % self.id
        
AccountRegistry.register(SystemAccount)
        
        
class UserAccount(Account):
    """
    Generic User account.
    This holds user profile as well!.
    
    A user account has languages defined so that it primarily 'sees' his favorite languages.
    """
    user = models.OneToOneField(User, unique=True, related_name = "useraccount")

    is_user_account = True

    def save(self, *args, **kw):
        """
        Set the 'name' attibute from User Source.
        We don't bother checking the security here, ther parent will do it.
        If this is a creation, ensure we join the GlobalCommunity as well.
        """
        from twistranet.models import community
        self.slug = self.user.username
        creation = not self.id
    
        # Actually supersave the account before joining glob. comm.
        ret = super(UserAccount, self).save(*args, **kw)
        if creation:
            glob = community.GlobalCommunity.objects.get()
            glob.join(self)
        
        return ret

    class Meta:
        app_label = 'twistranet'
        

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

        
AccountRegistry.register(UserAccount)

