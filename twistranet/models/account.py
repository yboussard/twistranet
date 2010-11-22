from django.db import models
from django.db.models import Q
from django.core.cache import cache
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation

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
    # XXX TODO: Definitely rename this into 'title'
    @property
    def screen_name(self):
        return self.title
                                            
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
        
        # Validate screen_name / slug
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

    def has_role(self, role, obj = None, obj_id = None):
        """
        Return if SELF account has the given role on the given object.
        XXX TODO Heavily uses caching and optimize queries
        XXX TODO Make only one query for db-dependant roles?
        Some roles are global (authenticated, anonymous, administrator, ..), 
        and some are dependent of the given object (community_member, ...).
        
        Warning: This method can return different results when called
        from the authenticated user or not. We should only cache calls made
        from currently authenticated user.
        
        If a user has a role on an object, that doesn't means he has a permision...
        
        You can pass either an obj or a twistable id (to avoid dereferencing the
        underlying object if we can, for performance reasons).
        
        XXX TODO: Oh, BTW, we should check if the role actually exists!
        """
        auth = self
        if obj is None and obj_id is None:
            obj = self
        if obj_id is None:
            obj_id = obj.id
                
        # We've been given an id instead of an object:
        # Then we'll issue an explicit and possibly complex query to find the role.
        # if obj is None:
        # Oh, BTW, start by checking anonymous shortcut
        if isinstance(auth, SystemAccount):
            return True
        if isinstance(auth, AnonymousAccount):
            # XXX Can't be true, Anon. may not have owner or nwk roles!
            flt = twistable.Twistable.objects.get_anonymous_filter(auth)
            raise NotImplementedError("todo")
            
        # Procedural method if obj is already given.
        # We use this as a shortcut to avoid issuing costly queries.
        has_role = None
        if obj is not None:
            if role <= roles.owner:
                if obj.owner_id == auth.id:
                    has_role = True
                elif obj.publisher_id == auth.id:
                    has_role = True
                elif obj_id == auth.id:
                    has_role = True
                    
            if role <= roles.public:
                if not obj.publisher_id:
                    has_role = True
            
        # Didn't find the role. We must issue a query.
        if has_role is None:
            if role == roles.owner:
                flt = twistable.Twistable.objects.get_owner_filter(auth)
            elif role == roles.network:
                flt = twistable.Twistable.objects.get_network_filter(auth) | \
                    twistable.Twistable.objects.get_owner_filter(auth)
            elif role == roles.public:
                flt = twistable.Twistable.objects.get_public_filter(auth) | \
                    twistable.Twistable.objects.get_network_filter(auth) | \
                    twistable.Twistable.objects.get_owner_filter(auth)
            elif role == roles.system:
                return False        # System account must have been shunted before
            else:
                raise NotImplementedError("Role %s not implemented", role)
                
            # Issue the query to find role value
            # print "QUERY!", self, "has_role", role, "on", obj_id
            has_role = twistable.Twistable.objects.__booster__.filter(
                Q(id = obj_id,) & flt
            ).exists()
            
        return has_role

        # We shouldn't reach there
        raise RuntimeError("Unexpected role (%s) asked for object '%s' (%s)" % (role, obj and obj.__class__.__name__, obj and obj.id))


    def has_permission(self, permission, obj):
        """
        Return true if authenticated user has been granted the given permission on obj.
        XXX TODO: Heavily optimize and use caching!
        """
        """
        mgr = twistable.Twistable.objects
        auth = mgr._getAuthenticatedAccount()
        if isinstance(auth, SystemAccount):
            return True
        if isinstance(auth, AnonymousAccount):
            # XXX Can't be true, Anon. may not have owner or nwk roles!
            raise NotImplementedError("todo")
        return mgr.filter(
            Q(
                id = obj.id,
                _permissions__name = permission,
            ) & (
                mgr.get_owner_filter(auth) | \
                mgr.get_network_filter(auth) | \
                mgr.get_public_filter(auth)
            )
        ).exists()
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
        Return True if current user is in the admin community or is System
        """
        raise NotImplementedError()
        # return self.is_administrator
        return self.has_role(roles.administrator)


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
        )
        
    @property
    def communities(self):
        """
        Return communities this user is actually a member of.
        """
        from community import Community
        return Community.objects.filter(targeted_network__target__id = self.id)

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
        if creation:
            glob = community.GlobalCommunity.objects.get()
            __account__ = SystemAccount.objects.get()
            glob.join(self)
            del __account__
        return ret
        
    def getDefaultOwner(self,):
        from twistranet.models import community
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

        

