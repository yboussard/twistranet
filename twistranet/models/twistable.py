"""
Base of the securable (ie. directly accessible through the web), translatable and full-featured TN object.

A twist-able object in TN is an object which can be accessed safely from a view.
Normally, everything a view manipulates must be taken from a TN object.

Content, Accounts, MenuItems, ... are all Twistable objects.

This abstract class provides a lot of little tricks to handle view/model articulation,
such as the slug management, prepares translation management and so on.
"""

import inspect, pprint, pickle
from django.db import models
from django.db.models import Q, loading
from django.contrib.auth.models import User
from django.db.utils import DatabaseError
from django.utils.datastructures import SortedDict
from django.core.cache import cache
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.utils import html, translation
from twistranet.lib import roles, permissions, languages, utils

MAX_HEADLINE_LENGTH = 140

def get_twistable_category(object) :
    """
    Return the twistable category according to the kind of object it is.
    XXX TODO: Make this a method of the Twistable class
    """
    from twistranet.models import Content, Account, Community, Resource
    if issubclass(object.model_class, Content):
        return 'content'
    elif issubclass(object.model_class, Community):
        return 'community'
    elif issubclass(object.model_class, Account):
        return 'account'
    elif issubclass(object.model_class, Resource):
        return 'resource'
    raise NotImplementedError("Can't get twistable category for object %s" % object)


class TwistableManager(models.Manager):
    """
    It's the base of the security model!!
    """
    # Disabled for performance reasons.
    # use_for_related_fields = True

    def get_query_set(self):
        """
        Return a queryset of 100%-authorized objects. All (should) have the can_list perm to True.
        This is in fact a kind of 'has_permission(can_list)' method!
        
        This method WILL return duplicates. Use this if you don't want to check unicity of a content.
        """
        # Check for anonymous query
        import community, account, community
        auth = self._getAuthenticatedAccount()
        base_query_set = super(TwistableManager, self).get_query_set()
            
        # System account: return all objects without asking any question. And with all permissions set.
        if auth.id == account.SystemAccount.SYSTEMACCOUNT_ID:
            return base_query_set
            
        # XXX TODO: Make a special query for admin members? Or at least mgrs of the global community?
        # XXX Make this more efficient?
        # XXX Or, better, check if current user is manager of the owner ?
        if auth.id:
            managed_accounts = [auth.id, ]
        else:
            managed_accounts = []
        
        # XXX This try/except is there so that things don't get stucked during boostrap
        try:
            if auth.is_admin:
                return base_query_set
        except:
            print "DB error while checking AdminCommunity"
            return base_query_set

        # Regular check. Works for anonymous as well...
        network_ids = auth.network_ids
        qs = base_query_set.filter(
            Q(
                owner__id = auth.id,
                _p_can_list = roles.owner,
            ) | Q(
                _access_network__targeted_network__target = auth,
                _p_can_list = roles.network,
            ) | Q(
                _access_network__targeted_network__target = auth,
                _p_can_list = roles.public,
            ) | Q(
                # Anonymous stuff
                _access_network__isnull = True,
                _p_can_list = roles.public,
            )
        )
        return qs
                

    def _getAuthenticatedAccount(self):
        """
        Dig the stack to find the authenticated account object.
        Return either a (possibly generic) account object or None.
        
        Views with a "request" parameter magically works with that.
        If you want to use a system account, declare a '__account__' variable in your caller function.
        """
        # We dig into the stack frame to find the request object.
        from account import Account, AnonymousAccount, UserAccount

        frame = inspect.currentframe()
        try:
            while frame:
                next_found = False
                local_viewed = False
                for mbr in inspect.getmembers(frame):
                    if mbr[0] == 'f_locals':
                        local_viewed = True
                        _locals = mbr[1]
    
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
                
                        # Check for an __acount__ variable holding a generic Account object
                        if _locals.has_key('__account__') and isinstance(_locals['__account__'], Account):
                            return _locals['__account__']
                    
                        # Locals inspected and next found => break here
                        if next_found:
                            break
        
                    if mbr[0] == 'f_back':
                        # Inspect caller
                        next_found = True
                        frame = mbr[1]
                        if local_viewed:
                            break
                            
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
    slug = models.SlugField(unique = True, db_index = True, null = True)                 # XXX TODO: Have a more personalized slug field (allowing dots for usernames?)
    
    # This is a way to de-reference the underlying model rapidly
    app_label = models.CharField(max_length = 64, db_index = True)
    model_name = models.CharField(max_length = 64, db_index = True)
    # Pointer to the underlying account, to allow the filter to work with all derived objects.
    # is_community = models.BooleanField(default = False, db_index = True, )
    
    # Text representation of this content
    # Usually a twistable is represented that way:
    # (pict) HEADLINE
    # Summary summary summary [Read more]
    # We store summary and headline in DB for performance and searchability reasons.
    # Heavy @-querying will be done at save time, not at display-time.
    # Both of them can contain links and minimal HTML formating.
    # Never let your users edit those fields directly, as they'll be flagged as html-safe!
    # If you want to change behaviour of those fields, override the preprocess_xxx methods.
    html_headline = models.CharField(max_length = 140)          # The computed headline (a-little-bit-more-than-a-title) for this content.
    html_summary = models.CharField(max_length = 1024)          # The computed summary for this content.
    text_headline = models.CharField(max_length = 140)          # The computed headline (a-little-bit-more-than-a-title) for this content.
    text_summary = models.CharField(max_length = 1024)          # The computed summary for this content.
    
    # List of field name / generation method name. This is very useful when translating content.
    # See twistrans.lib for more information
    # XXX TODO: Document and/or rename that?
    auto_values = (
        ("html_headline", "preprocess_html_headline", ),
        ("text_headline", "preprocess_text_headline", ),
        ("html_summary", "preprocess_html_summary", ),
        ("text_summary", "preprocess_text_summary", ),
    )
    
    # Basic metadata shared by all Twist objects.
    # Title is mandatory.
    title = models.CharField(max_length = 255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now = True, db_index = True)
    language = models.CharField(
        max_length = 10,
        blank = True,
        choices = languages.available_languages,
        default = languages.available_languages[0][0],
        db_index = True,
        )
        
    # Performance optimizer : we store the publisher here so that we can de-reference it without getting the content object.
    # These are two security flags.
    #  The account this content is published for. 'NULL' means visible to AnonymousAccount.
    publisher = models.ForeignKey("Account", null = True, related_name = "published_twistables", db_index = True, ) 

    # Security / Role shortcuts. These are the ppl/account the Owner / Network are given to.
    # The account this object belongs to (ie. the actual author)
    owner = models.ForeignKey("Account", related_name = "by", db_index = True, )                               
    
    # Our security model.
    # XXX TODO: Use a foreign key instead with some clever checking? Or a specific PermissionField?
    # XXX because there's a problem here as choices cannot be re-defined for subclasses.
    permission_templates = ()       # Define this in your subclasses
    permissions = models.CharField(
        max_length = 32,
        db_index = True,
    )
    _access_network = models.ForeignKey("Account", null = True, related_name = "+", db_index = True, )
        
    # The permissions. It's strongly forbidden to edit those roles by hand, use the 'permissions' property instead.
    _p_can_view = models.IntegerField(default = 16, db_index = True)
    _p_can_edit = models.IntegerField(default = 16, db_index = True)
    _p_can_list = models.IntegerField(default = 16, db_index = True)
    _p_can_list_members = models.IntegerField(default = 16, db_index = True)
    _p_can_publish = models.IntegerField(default = 16, db_index = True)
    _p_can_join = models.IntegerField(default = 16, db_index = True)
    _p_can_leave = models.IntegerField(default = 16, db_index = True)
    _p_can_create = models.IntegerField(default = 16, db_index = True)

    @models.permalink
    def get_absolute_url(self):
        """
        XXX TODO: Make this a little more MVC with @permalink decorator
        See http://docs.djangoproject.com/en/dev/ref/models/instances/#get-absolute-url
        XXX TODO: Don't use the 'object' accessor but use a twistable_category attribute in some way
        (eg. twistable_category is one of 'Account', 'Content', 'Menu' or 'Resource')
        """
        category = get_twistable_category(self.object)
        viewbyslug = '%s_by_slug' % category
        viewbyid = '%s_by_id' % category
        if hasattr(self, 'slug') :
            if self.slug :
                return  (viewbyslug, [self.slug])
        return (viewbyid, [self.id])
            
    #                                                                   #
    #           Internal management, ensuring DB consistancy            #    
    #                                                                   #

    def save(self, *args, **kw):
        """
        Set various object attributes
        """
        import account, community
        
        # Check if we're saving a real object and not a generic Content one (which is prohibited).
        # This must be a programming error, then.
        # XXX TODO: Check that type doesn't change. Also check that if id is None, type is None as well.
        if self.__class__.__name__ == Twistable.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
            
        # Set information used to retreive the actual subobject
        self.model_name = self._meta.object_name
        self.app_label = self._meta.app_label
        # self.is_community = isinstance(self, community.Community)

        # Set owner, publisher upon object creation. Publisher is NEVER set as None by default.
        if self.id is None:
            self.owner = self.getDefaultOwner()
            if not self.publisher_id:
                self.publisher = self.getDefaultPublisher()
            else:
                if not self.publisher.can_publish:
                    raise PermissionDenied("You're not allowed to publish on %s" % self.publisher)
        else:
            # XXX TODO: Check that nobody sets /unsets the owner or the publisher of an object
            # raise PermissionDenied("You're not allowed to set the content owner by yourself.")
            pass
            
        # Check if publisher is set. Only GlobalCommunity may have its publisher to None to make a site visible on the internet.
        if not self.publisher_id:
            if not isinstance(self, community.GlobalCommunity) and not isinstance(self, account.SystemAccount):
                raise ValueError("Only the Global Community can have no publisher, not %s" % self)
    
        # Set permissions; we will apply them last to ensure we have an id
        if not self.permissions:
            perm_template = self.model_class.permission_templates
            if not perm_template:
                raise ValueError("permission_templates not defined on class %s" % self.__class__.__name__)
            self.permissions = perm_template.get_default()
        tpl = [ t for t in self.permission_templates.permissions() if t["id"] == self.permissions ]
        if not tpl:
            # Didn't find? We restore default setting. XXX Should log/alert something here!
            tpl = [ t for t in self.permission_templates.permissions() if t["id"] == self.model_class.permission_templates.get_default() ]
            print "Restoring default permissions. Problem here."
            print "Unable to find %s permission template %s in %s" % (self, self.permissions, self.permission_templates.perm_dict)
        for perm, role in tpl[0].items():
            if perm.startswith("can_"):
                setattr(self, "_p_%s" % perm, role)
                
        # Set headline and summary cached values
        self.html_headline = self.preprocess_html_headline()
        self.text_headline = self.preprocess_text_headline()
        self.html_summary = self.preprocess_html_summary()
        self.text_summary = self.preprocess_text_summary()
    
        # Check if we're creating or not
        if self.id:
            creation = False
        else:
            creation = True
            
        # Save and update access network information
        ret = super(Twistable, self).save(*args, **kw)
        self._update_access_network()
        return ret

    def _update_access_network(self, ):
        """
        Update hierarchy of driven objects.
        If save is False, won't save result (useful when save() is performed later)
        """
        # No id => this twistable doesn't control anything, we pass. Value will be set AFTER saving.
        import account
        if not self.id:
            raise ValueError("Can't set _access_network before saving the object.")
            
        # Update current object
        _current_access_network = self._access_network
        obj = self.object
        if self._p_can_list in (roles.owner, ):
            self._access_network = None
        elif self._p_can_list == roles.network:
            if isinstance(obj, account.Account):
                self._access_network = obj
            else:
                self._access_network = self.publisher
        elif self._p_can_list == roles.public:
            obj = obj.publisher
            while obj:
                if obj._p_can_list == roles.public:
                    obj = obj.publisher
                    continue
                elif obj._p_can_list in (roles.owner, roles.network, ):
                    self._access_network = obj
                    break
                else:
                    raise ValueError("Unexpected can_list role found: %d on object %s" % (obj._p_can_list, obj))
        else:
            raise ValueError("Unexpected can_list role found: %d on object %s" % (obj._p_can_list, obj))

        # Update this object itself
        super(Twistable, self).save()

        # Update dependant objects if current object's network changed for public role
        Twistable.objects.__booster__.filter(
            Q(_access_network__id = self.id) | Q(publisher = self.id),
            _p_can_list = roles.public,
        ).update(_access_network = obj)
            
        # Special case: if the global community is not anonymously-available anymore,
        # we need to do this additional query to update "None" objects.
        # XXX TODO
            
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
        if self.slug:
            return "%s.%s: %s (%i)" % (self.app_label, self.model_name, self.slug, self.id)
        else:
            return "%s.%s: %i" % (self.app_label, self.model_name, self.id)            
            
    class Meta:
        app_label = "twistranet"



    #                                                               #
    #                       Display management                      #
    # You can override this in your content types.                  #
    #                                                               #

    def preprocess_html_headline(self, text = None):
        """
        preprocess_html_headline => unicode string.

        Used to compute the headline displayed.
        You can have some logic to display a different headline according to the content's properties.
        Default is to display the first characters (or so) of the title, or of raw text content if title is empty.

        You can override this in your own content types if you want.
        """
        if text is None:
            text = getattr(self, "title", "")
        if not text:
            text = getattr(self, "text", "")
        original_text = text
        headline_length = MAX_HEADLINE_LENGTH

        # Ensure headline will never exceed MAX_HEADLINE_LENGTH characters
        while True:
            text = html.escape(original_text)
            if len(text) >= headline_length:
                text = u"%s [...]" % text[:headline_length]
            text = utils.escape_links(text)
            if len(text) <= MAX_HEADLINE_LENGTH:
                break
            headline_length = headline_length - 5

        return text

    def preprocess_text_headline(self, text = None):
        """
        Default is just tag-stripping
        """
        if text is None:
            text = self.preprocess_html_headline()
        return html.strip_tags(text)

    def preprocess_html_summary(self, text = None):
        """
        Return an HTML-safe summary.
        Default is to keep the 1024-or-so first characters and to keep basic HTML formating.
        """
        if text is None:
            text = getattr(self, "description", "")
        if not text:
            text = getattr(self, "text", "")

        MAX_SUMMARY_LENGTH = 1024 - 10
        text = html.escape(text)
        if len(text) >= MAX_SUMMARY_LENGTH:
            text = u"%s [...]" % text[:MAX_SUMMARY_LENGTH]
        text = utils.escape_links(text)
        if text == self.preprocess_html_headline():
            text = ""

        return text

    def preprocess_text_summary(self, text = None):
        """
        Default is just tag-stripping
        """
        if text is None:
            text = self.preprocess_html_summary()
        return html.strip_tags(text)        

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


    #                                                                   #
    #                       Translation management                      #
    #                                                                   #
    
    @property
    def translation(self,):
        """
        Return the translated version of the content.
        Example: doc.translated.title => Return the translated version of the title.
        Use this in your templates. Use the _translated() method below in your python code or your tests.
        Please note that this doesnt de-reference your original object: you still have to de-reference it with content.object
        to get it. But you'll have access to translated fields anyway with the parent Content object.
        
        The translation object is always read-only!
        
        XXX TODO: Keep this in cache to avoid overhead
        """
        return self._translation(None)
    
    def _translation(self, language = None):
        """
        Return the translated version of your content.
        Example: doc.translated('fr').title => Return the translated version of the title.
        """
        return self
        
        # No translation available? Return the identity object.
        try:
            from twistrans.lib import _TranslationWrapper
        except ImportError:
            return self

        # If language is None, guess it
        if language is None:
            language = translation.get_language()
        
        # If language is the same as the content, return the content itself
        if language == self.language:
            return self
        
        # Return the wrapper around translated resources.
        if not hasattr(self, '_translation_cache'):
            self._translation_cache = _TranslationWrapper(self, language)
        return self._translation_cache
    
