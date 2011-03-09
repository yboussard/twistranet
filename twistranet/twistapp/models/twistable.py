"""
Base of the securable (ie. directly accessible through the web), translatable and full-featured TN object.

A twist-able object in TN is an object which can be accessed safely from a view.
Normally, everything a view manipulates must be taken from a TN object.

Content, Accounts, MenuItems, ... are all Twistable objects.

This abstract class provides a lot of little tricks to handle view/model articulation,
such as the slug management, prepares translation management and so on.
"""

import re
import inspect
import logging
import traceback
from django.db import models
from django.db.models import Q, loading
from django.db.utils import DatabaseError
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.utils.safestring import mark_safe

from  twistranet.twistapp.lib.log import log
from twistranet.twistapp.lib import roles, permissions
from twistranet.twistapp.lib.slugify import slugify
from twistranet.twistapp.signals import twistable_post_save
from fields import ResourceField, PermissionField, TwistableSlugField

class TwistableManager(models.Manager):
    """
    It's the base of the security model!!
    """
    # Disabled for performance reasons.
    # use_for_related_fields = True

    def get_query_set(self, __account__ = None, request = None, ):
        """
        Return a queryset of 100%-authorized objects. All (should) have the can_list perm to True.
        This is in fact a kind of 'has_permission(can_list)' method!
        
        This method IS very slow. But you can speed things up if you pass either 'request' or '__account__' along the lines.
        Be aware, however, that in this case you loose the 'safety belt' provided by the security model.
        """
        # Check for anonymous query
        import community, account, community
        __account__ = self._getAuthenticatedAccount(__account__, request)
        base_query_set = super(TwistableManager, self).get_query_set()
            
        # System account: return all objects without asking any question. And with all permissions set.
        if __account__.id == account.SystemAccount.SYSTEMACCOUNT_ID:
            return base_query_set
            
        # XXX TODO: Make a special query for admin members? Or at least mgrs of the global community?
        # XXX Make this more efficient?
        # XXX Or, better, check if current user is manager of the owner ?
        if __account__.id > 0:
            managed_accounts = [__account__.id, ]
        else:
            managed_accounts = []
        
        # XXX This try/except is there so that things don't get stucked during boostrap
        try:
            if __account__.is_admin:
                return base_query_set.filter(
                    _p_can_list__lte = roles.manager,
                )
        except DatabaseError:
            log.warning("DB error while checking AdminCommunity. This is NORMAL during syncdb or bootstrap.")
            return base_query_set

        # Regular check. Works for anonymous as well...
        # network_ids = __account__.network_ids
        if not __account__.is_anonymous:
            qs = base_query_set.filter(
                Q(
                    owner__id = __account__.id,
                    _p_can_list = roles.owner,
                ) | Q(
                    _access_network__targeted_network__target = __account__,
                    _p_can_list = roles.network,
                ) | Q(
                    _access_network__targeted_network__target = __account__,
                    _p_can_list = roles.public,
                ) | Q(
                    # Anonymous stuff
                    _access_network__isnull = True,
                    _p_can_list = roles.public,
                )
            )
        else:
            # Anon query. Easy: We just return public stuff.
            # Warning: nested query is surely inefficient...
            free_access_network = Twistable.objects.__booster__.filter(
                _access_network__isnull = True,
                _p_can_list = roles.public,
            )
            qs = base_query_set.filter(
                Q(
                    # Strictly anonymous stuff
                    _access_network__isnull = True,
                    _p_can_list = roles.public,
                ) | Q(
                    # Incidently anonymous stuff (public stuff published by an anon account)
                    _access_network__isnull = False,
                    _access_network__id__in = free_access_network,
                    _p_can_list = roles.public,
                )
            )
        return qs
                
    def getCurrentAccount(self, request):
        """
        The official and hassle-free method of getting the currently auth account from a view.
        Just pass the request object.
        """
        from account import Account, AnonymousAccount, UserAccount
        u = getattr(request, 'user', None)
        if isinstance(u, User):
            # We use this instead of the get_profile() method to avoid an infinite recursion here.
            # We mimic the _profile_cache behavior of django/contrib/auth/models.py to avoid doing a lot of requests on the same object
            if not hasattr(u, '_account_cache'):
                u._account_cache = UserAccount.objects.__booster__.get(user__id__exact = u.id)
                u._account_cache.user = u
            return u._account_cache

        # Didn't find anything. We must be anonymous.
        return AnonymousAccount()
                
    def _getAuthenticatedAccount(self, __account__ = None, request = None):
        """
        Dig the stack to find the authenticated account object.
        Return either a (possibly generic) account object or None.
        
        Views with a "request" parameter magically works with that.
        If you want to use a system account, declare a '__account__' variable in your caller function.
        """
        from account import Account, AnonymousAccount, UserAccount

        # If we have the __account__ object, then it's quite obvious here...
        if isinstance(__account__, Account):
            return __account__
            
        # If we have the request object, then we just can use getCurrentAccount() instead
        if request:
            return self.getCurrentAccount(request)

        # We dig into the stack frame to find the request object.
        frame = inspect.currentframe()
        try:
            while frame:
                frame_members = dict(inspect.getmembers(frame))
                
                # Inspect 'locals' variables to get the request or __account__
                _locals = frame_members.get('f_locals', None)
                if _locals:
                    # Check for an __acount__ variable holding a generic Account object. It always has precedence over 'request'
                    if _locals.has_key('__account__') and isinstance(_locals['__account__'], Account):
                        return _locals['__account__']
                
                    # Check for a request.user User object
                    if _locals.has_key('request'):
                        u = getattr(_locals['request'], 'user', None)
                        if isinstance(u, User):
                            # We use this instead of the get_profile() method to avoid an infinite recursion here.
                            # We mimic the _profile_cache behavior of django/contrib/auth/models.py to avoid doing a lot of requests on the same object
                            if not hasattr(u, '_account_cache'):
                                u._account_cache = UserAccount.objects.__booster__.get(user__id__exact = u.id)
                                u._account_cache.user = u
                            return u._account_cache
            
                # Get back to the upper frame
                frame = frame_members.get('f_back', None)
                        
            # Didn't find anything. We must be anonymous.
            return AnonymousAccount()

        finally:
            # Avoid circular refs
            frame = None
            stack = None
            del _locals


    # Backdoor for performance purposes. Use it at your own risk as it breaks security.
    @property
    def __booster__(self):
        return super(TwistableManager, self).get_query_set()

    @property
    def can_create(self,):
        auth = self._getAuthenticatedAccount()
        return not auth.is_anonymous


class _AbstractTwistable(models.Model):
    """
    We use this abstract class to enforce use of our manager in all our subclasses.
    """
    objects = TwistableManager()
    class Meta:
        abstract = True

class Twistable(_AbstractTwistable):
    """
    Base (an abstract) type for rich, inheritable and securable TN objects.
    
    This class is quite optimal when using its base methods but you should always use
    your dereferenced class when you can do so!
    
    All Content and Account classes derive from this.
    XXX TODO: Securise the base manager!
    """
    # Object management. Slug is optional (id is not ;))
    slug = TwistableSlugField(unique = True, db_index = True, null = True, blank = True)
        
    # This is a way to de-reference the underlying model rapidly
    app_label = models.CharField(max_length = 64, db_index = True)
    model_name = models.CharField(max_length = 64, db_index = True)
    
    # Text representation of this content
    # Usually a twistable is represented that way:
    # (pict) TITLE
    # Description [Read more]
        
    # Basic metadata shared by all Twist objects.
    # Title is mandatory!
    title = models.CharField(max_length = 255, blank = True, default = '')
    description = models.TextField(max_length = 1024, blank = True, default = '')
    created_at = models.DateTimeField(auto_now_add = True, null = True, db_index = False)
    modified_at = models.DateTimeField(auto_now = True, null = True, db_index = True)
    created_by = models.ForeignKey("Account", related_name = "created_twistables", db_index = True, ) 
    modified_by = models.ForeignKey("Account", null = True, related_name = "modified_twistables", db_index = True, ) 
    
    # Picture management.
    # If None, will use the default_picture_resource_slug attribute.
    # If you want to get the account picture, use the 'picture' attribute.
    default_picture_resource_slug = None
    # XXX TODO PJ : the widget params are never rendered
    picture = ResourceField( media_type='image', null = True, blank = True, related_name = "picture_of")
    tags = models.ManyToManyField("Tag", related_name = "tagged")
    
    # These are two security flags.
    #  The account this content is published for. 'NULL' means visible to AnonymousAccount.
    publisher = models.ForeignKey("Account", null = True, blank = True, related_name = "published_twistables", db_index = True, ) 

    # Security / Role shortcuts. These are the ppl/account the Owner / Network are given to.
    # The account this object belongs to (ie. the actual author)
    owner = models.ForeignKey("Account", related_name = "by", db_index = True, )                               
    
    # Our security model.
    permission_templates = ()       # Define this in your subclasses
    permissions = PermissionField(db_index = True)
    _access_network = models.ForeignKey("Account", null = True, blank = True, related_name = "+", db_index = True, )
        
    # The permissions. It's strongly forbidden to edit those roles by hand, use the 'permissions' property instead.
    _p_can_view = models.IntegerField(default = 16, db_index = True)
    _p_can_edit = models.IntegerField(default = 16, db_index = True)
    _p_can_list = models.IntegerField(default = 16, db_index = True)
    _p_can_list_members = models.IntegerField(default = 16, db_index = True)
    _p_can_publish = models.IntegerField(default = 16, db_index = True)
    _p_can_join = models.IntegerField(default = 16, db_index = True)
    _p_can_leave = models.IntegerField(default = 16, db_index = True)
    _p_can_create = models.IntegerField(default = 16, db_index = True)
    
    # Other configuration stuff (class-wise)
    _ALLOW_NO_PUBLISHER = False         # Prohibit creation of an object of this class with publisher = None.
    _FORCE_SLUG_CREATION = True         # Force creation of a slug if it doesn't exist
    
    @property
    def kind(self):
        """
        Return the kind of object it is (as a lower-cased string).
        """
        from twistranet.twistapp.models import Content, Account, Community, Resource
        from twistranet.tagging.models import Tag
        mc = self.model_class
        if issubclass(mc, Content):
            return 'content'
        elif issubclass(mc, Community):
            return 'community'
        elif issubclass(mc, Account):
            return 'account'
        elif issubclass(mc, Resource):
            return 'resource'
        elif issubclass(mc, Tag):
            return 'tag'
        raise NotImplementedError("Can't get twistable category for object %s" % self)

    @models.permalink
    def get_absolute_url(self):
        """
        return object absolute_url
        """
        category = self.kind
        viewbyslug = '%s_by_slug' % category
        viewbyid = '%s_by_id' % category
        if hasattr(self, 'slug'):
            if self.slug:
                return  (viewbyslug, [self.slug])
        return (viewbyid, [self.id])

    @property
    def html_link(self,):
        """
        Return a pretty HTML anchor tag
        """
        d = {
            'label': self.title_or_description,
            'url': self.get_absolute_url(),
        }
        return u"""<a href="%(url)s" title="%(label)s">%(label)s</a>""" % d
        
    @property
    def forced_picture(self,):
        """
        Return actual picture for this content or default picture if not available.
        May return None!
        XXX SHOULD CACHE THIS
        """
        import resource
        if issubclass(self.model_class, resource.Resource):
            return self
        try:
            picture = self.picture
            if picture is None:
                raise resource.Resource.DoesNotExist()
        except resource.Resource.DoesNotExist:
            try:
                picture = resource.Resource.objects.get(slug = self.model_class.default_picture_resource_slug)
            except resource.Resource.DoesNotExist:
                return None
        return picture
        
    def get_thumbnail(self, *args, **kw):
        """
        Same arguments as sorl's get_thumbnail method.
        """
        from sorl.thumbnail import default
        return default.backend.get_thumbnail(self.forced_picture.image, *args, **kw)
        
    @property
    def thumbnails(self,):
        """
        Return a dict of standard thumbnails methods.
        XXX TODO: Cache this! And use lazy resolution!
        Some day resources will be able to have several DIFFERENT previews...
        
        Preview: Max = 500x500; Used when a large version should be available.
        Summary: Max = 100x100;
        Summary Preview: Max = Min = 100x100;
        Medium:  Max = Min = 50x50;
        Icon:    Max = Min = 16x16;
        """
        return {
            "preview":           self.get_thumbnail("500x500", crop = "", upscale = False),
            "summary":           self.get_thumbnail("100x100", crop = "", upscale = False),
            "summary_preview":   self.get_thumbnail("100x100", crop = "center top", upscale = True),
            "medium":            self.get_thumbnail("50x50", crop = "center top", upscale = True),
            "big_icon":          self.get_thumbnail("32x32", upscale = False),
            "icon":              self.get_thumbnail("16x16", crop = "center top", upscale = True),
        }
                
            
    #                                                                   #
    #           Internal management, ensuring DB consistancy            #    
    #                                                                   #

    def save(self, *args, **kw):
        """
        Set various object attributes
        """
        import account
        import community
        
        auth = Twistable.objects._getAuthenticatedAccount()

        # Check if we're saving a real object and not a generic Content one (which is prohibited).
        # This must be a programming error, then.
        if self.__class__.__name__ == Twistable.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
            
        # Set information used to retreive the actual subobject
        self.model_name = self._meta.object_name
        self.app_label = self._meta.app_label

        # Set owner, publisher upon object creation. Publisher is NEVER set as None by default.
        if self.id is None:
            # If self.owner is already set, ensure it's done by SystemAccount
            if self.owner_id:
                if not isinstance(auth, account.SystemAccount):
                    raise PermissionDenied("You're not allowed to set the content owner by yourself.")
            else:
                self.owner = self.getDefaultOwner()
            if not self.publisher_id:
                self.publisher = self.getDefaultPublisher()
            else:
                if not self.publisher.can_publish:
                    raise PermissionDenied("You're not allowed to publish on %s" % self.publisher)
        else:
            # XXX TODO: Check that nobody sets /unsets the owner or the publisher of an object
            # raise PermissionDenied("You're not allowed to set the content owner by yourself.")
            if not self.can_edit:
                raise PermissionDenied("You're not allowed to edit this content.")
            
        # Set created_by and modified_by fields
        if self.id is None:
            self.created_by = auth
        self.modified_by = auth
            
        # Check if publisher is set. Only GlobalCommunity may have its publisher to None to make a site visible on the internet.
        if not self.publisher_id:
            if not self.__class__._ALLOW_NO_PUBLISHER:
                raise ValueError("Only the Global Community can have no publisher, not %s" % self)
    
        # Set permissions; we will apply them last to ensure we have an id.
        # We also ensure that the right permissions are set on the right object
        if not self.permissions:
            perm_template = self.model_class.permission_templates
            if not perm_template:
                raise ValueError("permission_templates not defined on class %s" % self.__class__.__name__)
            self.permissions = perm_template.get_default()
        tpl = [ t for t in self.permission_templates.permissions() if t["id"] == self.permissions ]
        if not tpl:
            # Didn't find? We restore default setting. XXX Should log/alert something here!
            tpl = [ t for t in self.permission_templates.permissions() if t["id"] == self.model_class.permission_templates.get_default() ]
            log.warning("Restoring default permissions. Problem here.")
            log.warning("Unable to find %s permission template %s in %s" % (self, self.permissions, self.permission_templates.perm_dict))
        if tpl[0].get("disabled_for_community") and issubclass(self.publisher.model_class, community.Community):
            raise ValueError("Invalid permission setting %s for this object (%s/%s)" % (tpl, self, self.title_or_description))
        elif tpl[0].get("disabled_for_useraccount") and issubclass(self.publisher.model_class, account.UserAccount):
            raise ValueError("Invalid permission setting %s for this object (%s/%s)" % (tpl, self, self.title_or_description))
        for perm, role in tpl[0].items():
            if perm.startswith("can_"):
                if callable(role):
                    role = role(self)
                setattr(self, "_p_%s" % perm, role)

        # Check if we're creating or not
        created = not self.id
                
        # Generate slug (or not !)
        if not self.slug and self.__class__._FORCE_SLUG_CREATION:
            if self.title:
                self.slug = slugify(self.title)
            elif self.description:
                self.slug = slugify(self.description)
            else:
                self.slug = slugify(self.model_name)
            self.slug = self.slug[:40]
        if created and self.__class__._FORCE_SLUG_CREATION:
            while Twistable.objects.__booster__.filter(slug = self.slug).exists():
                match = re.search("_(?P<num>[0-9]+)$", self.slug)
                if match:
                    root = self.slug[:match.start()]
                    num = int(match.groupdict()['num']) + 1
                else:
                    root = self.slug
                    num = 1
                self.slug = "%s_%i" % (root, num, )
        
        # Perform a full_clean on the model just to be sure it validates correctly
        self.full_clean()
            
        # Save and update access network information
        ret = super(Twistable, self).save(*args, **kw)
        self._update_access_network()

        # Send TN's post-save signal
        twistable_post_save.send(sender = self.__class__, instance = self, created = created)
        return ret

    def _update_access_network(self, ):
        """
        Update hierarchy of driven objects.
        If save is False, won't save result (useful when save() is performed later).
        """
        # No id => this twistable doesn't control anything, we pass. Value will be set AFTER saving.
        import account, community
        if not self.id:
            raise ValueError("Can't set _access_network before saving the object.")
            
        # Update current object. We save current access and determine the more restrictive _p_can_list access permission.
        # Remember that a published content has its permissions determined by its publisher's can_VIEW permission!
        _current_access_network = self._access_network
        obj = self.object
        if issubclass(obj.model_class, account.Account):
            _p_can_list = self._p_can_list
        else:
            _p_can_list = max(self._p_can_list, self.publisher and self.publisher._p_can_view or roles.public)
        
        # If restricted to content owner, no access network mentionned here.
        if _p_can_list in (roles.owner, ):
            self._access_network = None     # XXX We have to double check this, esp. on the GlobalCommunity object.
            
        # Network role: same as current network for an account, same as publisher's network for a content
        elif _p_can_list == roles.network:
            if issubclass(obj.model_class, account.Account):
                self._access_network = obj
            else:
                self._access_network = self.publisher
            
        # Public content (or so it seems)
        elif _p_can_list == roles.public:
            # GlobalCommunity special case: if can_list goes public, then we can unrestrict the _access_network
            if issubclass(self.model_class, community.GlobalCommunity):
                self._access_network = None     # Let's go public!
                
            else:
                # Regular treatment
                obj = obj.publisher
                while obj:
                    if obj._p_can_list == roles.public:
                        if obj == obj.publisher:
                            # If an object is its own publisher (eg. GlobalCommunity),
                            # we avoid infinite recursions here.
                            break
                        obj = obj.publisher
                    elif obj._p_can_list in (roles.owner, roles.network, ):
                        self._access_network = obj
                        break
                    else:
                        raise ValueError("Unexpected can_list role found: %d on object %s" % (obj._p_can_list, obj))
        else:
            raise ValueError("Unexpected can_list role found: %d on object %s" % (obj._p_can_list, obj))

        # Update this object itself without calling the save() method again
        Twistable.objects.__booster__.filter(id = self.id).update(_access_network = self._access_network)

        # Update dependant objects if current object's network changed for public role
        Twistable.objects.__booster__.filter(
            Q(_access_network__id = self.id) | Q(publisher = self.id),
            _p_can_list = roles.public,
        ).exclude(id = self.id).update(_access_network = obj)
        
        # This is an additional check to ensure that no _access_network = None object with _p_can_list|_p_can_view = public still remains
        # glob = community.GlobalCommunity.get()
        # Twistable.objects.__booster__.filter(
        #     _access_network__isnull = True,
        #     _p_can_list = roles.public
        # ).update(_access_network = glob)
            
    def delete(self,):
        """
        Here we avoid deleting related object for nullabled ForeignKeys.
        XXX This is bad 'cause if we use the Manager.delete() method, this won't get checked!!!
        XXX We need to migrate to Django 1.3 ASAP to get this issue solved with the on_delete attribute.
        
        Hack from http://djangosnippets.org/snippets/1231/
        """
        self.clear_nullable_related()
        super(Twistable, self).delete()

    def clear_nullable_related(self):
        """
        Recursively clears any nullable foreign key fields on related objects.
        Django is hard-wired for cascading deletes, which is very dangerous for
        us. This simulates ON DELETE SET NULL behavior manually.
        """
        # Update picture__id
        Twistable.objects.__booster__.filter(picture__id = self.id).update(
            picture = None
        )

    @property
    def model_class(self):
        """
        Return the actual model's class.
        This method issues no DB query.
        """
        return loading.get_model(self.app_label, self.model_name)
        
    @property
    def object(self):
        """
        Return the exact subclass this object belongs to.
        
        IT MAY ISSUE DB QUERY, so you should always consider using model_class instead if you can.
        This is quite complex actually: since we want like to minimize database overhead,
        we can't allow a "Model.objects.get(id = x)" call.
        So, instead, we walk through object inheritance to fetch the right attributes.
        
        XXX TODO: This is where I can implement the can_view or can_list filter. See search results to understand why.
        """
        if self.id is None:
            raise RuntimeError("You can't get subclass until your object is saved in database.")

        # Get model class directly
        model = loading.get_model(self.app_label, self.model_name)
        if isinstance(self, model):
            return self
        return model.objects.__booster__.get(id = self.id)
            
    def __unicode__(self,):
        """
        Return model_name: id (slug)
        """
        if not self.app_label or not self.model_name:
            return "Unsaved %s" % self.__class__
        if not self.id:
            return "Unsaved %s.%s" % (self.app_label, self.model_name, )
        if self.slug:
            return "%s.%s: %s (%i)" % (self.app_label, self.model_name, self.slug, self.id)
        else:
            return "%s.%s: %i" % (self.app_label, self.model_name, self.id)
        
    @property    
    def title_or_description(self):
        """
        Return either title or description (or slug) but avoid the empty string at all means.
        The return value is considered HTML-safe.
        """
        for attr in ('title', 'description', 'slug', 'id'):
            v = getattr(self, attr, None)
            if not v:
                continue
            if not isinstance(v, unicode):
                v = unicode(v, errors = 'ignore')
            return mark_safe(v)
            
    class Meta:
        app_label = 'twistapp'


    #                                                                   #
    #                       Security Management                         #
    #                                                                   #
    # XXX TODO: Use a more generic approach? And some caching as well?  #
    # XXX Also, must check that permissions are valid for the given obj #
    #                                                                   #

    def getDefaultOwner(self,):
        """
        General case: owner is the auth account (or SystemAccount if not found?)
        """
        return Twistable.objects._getAuthenticatedAccount()
        
    def getDefaultPublisher(self,):
        """
        General case: publisher is the auth account (or SystemAccount if not found?)
        """
        return Twistable.objects._getAuthenticatedAccount()

    @property
    def can_view(self):
        if not self.id: return  True        # Can always view an unsaved object
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_view, self)

    @property
    def can_delete(self):
        if not self.id: return  True        # Can always delete an unsaved object
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_delete, self)

    @property
    def can_edit(self):
        if not self.id: return  True        # Can always edit an unsaved object
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_edit, self)

    @property
    def can_publish(self):
        """
        True if authenticated account can publish on the current account object
        """
        if not self.id: return  False        # Can NEVER publish an unsaved object
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_publish, self)

    @property
    def can_list(self):
        """
        Return true if the current account can list the current object.
        """
        if not self.id: return  True        # Can always list an unsaved object
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_list, self)

    #                                                                   #
    #                           Views relations                         #
    #                                                                   #

    @property
    def summary_view(self):
        return self.model_class.type_summary_view

    @property
    def detail_view(self):
        return self.model_class.type_detail_view


