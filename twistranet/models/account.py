from django.db import models
from django.db.models import Q
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation

from twistranet import twistranet_settings as settings
import twistable
from resource import Resource
from twistranet.lib import permissions, roles, languages, utils

# Create your models here.
class Account(twistable.Twistable):
    """
    A generic account.
    This is an abstract class.
    Can be subclassed as a user account, group account, app account, etc
    """                                        
    # Picture management.
    # If None, will use the default_picture_resource_slug attribute.
    # If you want to get the account picture, use the 'picture' attribute.
    default_picture_resource_slug = "default_profile_picture"
    picture = models.ForeignKey("Resource")        # Ok, this is odd but it's because of the bootstrap.
                                                    # XXX We should avoid the 'null' attribute someday. Not easy 'cause of the SystemAccount bootstraping...

    # Security models available for the user
    # XXX TODO: Use a foreign key instead with some clever checking? Or a specific PermissionField?
    # XXX because there's a problem here as choices cannot be re-defined for subclasses.
    permission_templates = permissions.account_templates
    
    # View overriding support
    type_summary_view = "account/summary.part.html"
    
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
        XXX TODO: Check saving rights
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
            self.slug = utils.slugify(self.title)
            
        # Set default picture if not set (and if available)
        if not self.picture_id: # and not self.object_type == 'SystemAccount':
            self.picture = Resource.objects.__booster__.get(slug = self.default_picture_resource_slug)
                    
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
        # XXX TODO
        if role == roles.managers:
            raise NotImplementedError()
        
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
        p_template = obj.model_class.permission_templates.get(obj.permissions)
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
        self._is_admin = community.AdminCommunity.objects.__booster__.get().is_member
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
        )
        
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
    def network_for_display(self,):
        """
        Used to display network information. Heavily cached and cleverly sorted.
        """
        return self.network.order_by("-id")[:settings.TWISTRANET_FRIENDS_IN_BOXES]
    
    def follow(self, account):
        """
        Ask this account to follow another one.
        """
        # XXX TODO: CHECK SECURITY HERE!
        from twistranet.models.network import Network
        me_to_you = Network.objects.filter(client = self, target = account)
        if me_to_you.exists():
            # Already exists
            return
        
        # If the given account already follows me, then we consider the relation as approved
        you_to_me = Network.objects.filter(client = account, target = self)
        if you_to_me.exists():
            you_to_me = you_to_me.get()
            # you_to_me.approved = True
            you_to_me.save()
            approved = True
        elif account.id == self.id:
            approved = True
        else:
            approved = False
        me_to_you = Network(client = self, target = account, )#approved = approved)
        me_to_you.save()
    
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
        return Community.objects.filter(targeted_network__target__id = self.id)

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


class AnonymousAccount(Account):
    """
    Representation of an anonymous account.
    Never instanciate that directly, the _getAuthenticatedAccount() takes care for you.
    
    Note that there is an AnonymousAccount table in DB, unfortunately :(
    """
    is_anonymous = True
    class Meta:
        # abstract = True
        app_label = "twistranet"
        managed=False

    def save(self, *args, **kw):
        """
        Prohibit object saving.
        """
        raise RuntimeError("You're not allowed to save or edit the anonymous account.")
        
class SystemAccount(Account):
    """
    The system accounts for TwistraNet.
    There must be at least 1 system account called '_system'. It's its role to build initial content.
    System accounts can reach ALL content from ALL communities.
    """
    default_picture_resource_slug = "default_system_picture"
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

    def save(self, *args, **kw):
        """
        Set the 'name' attibute from User Source.
        We don't bother checking the security here, the parent will do it.
        If this is a creation, ensure we join the GlobalCommunity as well.
        """
        from twistranet.models import community
        if not self.slug:
            self.slug = self.user.username
        creation = not self.id
        ret = super(UserAccount, self).save(*args, **kw)

        # Join the global community. For security reasons, it's SystemAccount who does this.
        # Add myself to my own community as well.
        if creation:
            glob = community.GlobalCommunity.objects.get()
            __account__ = SystemAccount.objects.get()
            glob.join(self)
            self.follow(self)
            self.save()
            del __account__
        return ret
        
    def getDefaultOwner(self,):
        return SystemAccount.get()
        return community.AdminCommunity.objects.get()
        
    def getDefaultPublisher(self,):
        from twistranet.models import community
        return community.GlobalCommunity.objects.get()

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

        

