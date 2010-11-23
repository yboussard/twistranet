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
from django.core.cache import cache
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.utils import html, translation
from twistranet.lib import roles, permissions, languages, utils

class TwistableManager(models.Manager):
    """
    It's the base of the security model!!
    
    The base manager assumes that:
    - it's called from a view having an authenticated user
    - its target model has a manager called _objects which return the unprotected objects.
    - the target model has a 'scope' property which is used to define the model's object visibility.
        Must be one of ACCOUNTSCOPE_ANONYMOUS, ACCOUNTSCOPE_AUTHENTICATED or ACCOUNTSCOPE_MEMBERS for account
        or must be CONTENTSCOPE_PUBLIC, CONTENTSCOPE_NETWORK or CONTENTSCOPE_PRIVATE for content
    """
    # Disabled for performance reasons.
    # use_for_related_fields = True
    
    def get_anonymous_filter(self, auth = None, ):
        """
        Return only visible-to-anonymous objects.
        It's easy:
          a/ The SystemAccount (always visible)
          b/ publisher = None 
          c/ objects with perm = public and publisher's publisher = None.
        """
        if auth is None:
            auth = self._getAuthenticatedAccount()

        return Q(
            # We use this supplementary query because permissions are not implemented in the JSON fixture for system
            app_label = "twistranet",
            model_name = "SystemAccount",
        ) | Q(
            _p_can_list = roles.public,
            publisher__id = None,
        ) | Q(
            _p_can_list = roles.public,
            publisher___p_can_view = roles.public,
            publisher__publisher__isnull = True,
        )

    def get_public_filter(self, auth = None):
        """
        1- A 'public' role is granted to me on an object if either:
           a/ the object's publisher is None (in this case, the "public" role is given to anonymous users as well)
           b/ the object's publisher is in can_view = public ;
           c/ the object's publisher is in can_view = network and publisher is in my network ;
        """
        if auth is None:
            auth = self._getAuthenticatedAccount()
        
        return (
            Q(
                _p_can_list = roles.public,
                publisher__id = None,
            ) | Q(
                _p_can_list = roles.public,
                publisher___p_can_view = roles.public,
            ) | Q(
                _p_can_list = roles.public,
                publisher___p_can_view = roles.network,
                publisher__targeted_network__target = auth,
            )
        )

    def get_network_filter(self, auth = None, ):
        """
        # 2- A 'network' role is granted to me on an object if (the subtelty here is that non-account do not have a network):
        #   a/ the object IS an Account AND i'm in the object's network ;
        #   b/ the object is NOT an Account and the object's publisher can_view is (network or public) and publisher is in my network ;
        """
        if auth is None:
            auth = self._getAuthenticatedAccount()
        
        return Q(
            _p_can_list__lte = roles.network,
            account_object__isnull = False,
            account_object__targeted_network__target = auth,
        ) | Q(
            _p_can_list__lte = roles.network,
            account_object__isnull = True,
            publisher__targeted_network__target = auth,
        )

    def get_owner_filter(self, auth = None, ):
        """
        # 3- An 'owner' role is granted to me on an object if:
        #   a/ the object's owner is me
        #   b/ I own the object's publisher ; this way I can always see what's published on me ;
        #   c/ I AM the objec's publisher (same idea as c/)
        #   d/ I'm a member of its owner (useful for communities)
        #   e/ ME ;)
        """
        if auth is None:
            auth = self._getAuthenticatedAccount()
        
        return Q(
            id = auth.id,
        ) | Q(
            owner = auth,
        ) | Q(
            publisher = auth,
        ) | Q(
            publisher__owner = auth,
        ) | Q(
            owner__targeted_network__target = auth,
            owner__is_community = True,
        )

    def duplicate_query_set(self):
        """
        Return a queryset of 100%-authorized objects. All (should) have the can_list perm to True.
        This is in fact a kind of 'has_permission(can_list)' method!
        
        This method WILL return duplicates. Use this if you don't want to check unicity of a content.
        """
        # Check for anonymous query
        import community, account
        auth = self._getAuthenticatedAccount()
        base_query_set = super(TwistableManager, self).get_query_set()
        
        # This is a performance boost for anonymous accounts: we don't bother computing ALL the filters.
        anon_filter = self.get_anonymous_filter(auth)
        if not auth or isinstance(auth, account.AnonymousAccount):
            try:
                return base_query_set.filter(anon_filter).distinct()        # XXX TODO: avoid this distinct() call
            except DatabaseError:
                # Avoid bootstrap quircks. XXX VERY DANGEROUS, should limit that to table doesn't exist errors!
                print "DB ERROR"
                return base_query_set.none()
    
        # System account: return all objects without asking any question.
        if auth.id == account.SystemAccount.SYSTEMACCOUNT_ID:
            return base_query_set.extra(select = {
                "_c_owner": "1 = 1",
                "_c_network": "1 = 1",
                "_c_public": "1 = 1",
            })
                        
        # Ok, so the struggle begins!
        #
        # Just to remember, basic roles are "public", "network", "owner" and "system".
        # What is used to find the role on an object is:
        #   - its 'publisher' account. The general rule here is that the publisher acts as a "filter" on an object's visibility.
        #       Unless you're the owner of an object, you can never get a more "powerful" role on an object than on it's publisher's.
        #       If publisher is None/Null then the object is visible EVEN TO ANONYMOUS. Careful, then!
        #       A content's publisher defines where it can be seen.
        #       An account can be its own publisher. This can be used to make an account less visible, but usually
        #       an account is published on a community (default is all_twistranet). This is a way to define the "homeland" of a UserAccount,
        #       and a way to have accounts who can't see/list between them.
        #       A User Source define where the UserAccounts are published by default. This is useful to given a common set of
        #       rights to all users coming from a same source (LDAP, SQL, ...)
        #       A Community's publisher can define a degree of "officialty" to the community.
        #       DEFAULT:
        #           - Content/Community:  default publisher = the auth account creating it.
        #           - UserAccount: default publisher = GlobalCommunity.
        #  - its network (for an account) or the publisher's NW (for a content).
        #       Beeing in the network usually give you some privileges. And more if the nwk relation has the is_manager flag.
        #  - its owner. The owner has the licence to kill on the object.
        #       An account is always his own owner!
        #       And you can add as an owner either the SystemAccount, a UserAccount or the AdminCommunity object.
        #       DEFAULT:
        #           - Non-UserAccount objects: owner = the authenticated user creating the content.
        #           - UserAccount: owner = AdminCommunity.
        
        # We should cache as much as we could.
        public_filter = self.get_public_filter(auth, )
        network_filter = self.get_network_filter(auth, )
        owner_filter = self.get_owner_filter(auth, )
        qs = base_query_set.filter(public_filter | network_filter | owner_filter)

        # We try to find the owner network table.
        # We use the find_ordering_name() method for that. Maybe that's too deep into Django guts?
        # XXX TODO: Cache this dict on a per-model basis?
        flt_qs = qs.filter()        # Make a copy to avoid trashing the original query_set
        select_field_keys = [
            "owner__id",
            "publisher__id",
            "account_object__id",
            "owner__is_community",
            "publisher__owner__id",
            "owner__targeted_network__target__id",
            "account_object__targeted_network__target__id",
            "publisher__targeted_network__target__id",
        ]
        select_field_keys.sort(lambda x,y: cmp(len(y), len(x)))
        select_fields = {}
        for fld in select_field_keys:
            if not "__" in fld:
                raise ValueError("Your field names must have __ in them: %s" % fld)
            actual_field = flt_qs.query.get_compiler(using = flt_qs.db).find_ordering_name(fld, flt_qs.query.model._meta)[0]
            # print fld, actual_field
            select_fields[fld] = "%s.%s" % (actual_field[0], actual_field[1], )
        
        param_dict = {
            "auth__id":             auth.id,
            "network_role":         roles.network,
        }
        select_dict = {
            "_c_owner": """
                twistranet_twistable.id = %(auth__id)d
                OR owner__id = %(auth__id)d
                OR publisher__id = %(auth__id)d
                OR publisher__owner__id = %(auth__id)d
                OR (
                    owner__targeted_network__target__id = %(auth__id)d
                    AND owner__is_community = 1
                )""" % param_dict,
            #     
            # "_c_network": """
            #     (
            #         twistranet_twistable._p_can_list <= %(network_role)d
            #         AND account_object__id IS NOT NULL
            #         AND account_object__targeted_network__target__id = %(auth__id)d
            #     ) OR (
            #         twistranet_twistable._p_can_list <= %(network_role)d
            #         AND account_object__id IS NULL
            #         AND publisher__targeted_network__target__id = %(auth__id)d
            #     )""" % param_dict,
        }
        
        # Replace select_dict values with the right field
        for s in select_dict.keys():
            select_dict[s] = select_dict[s].replace("\n", " ")
            select_dict[s] = select_dict[s].replace("  ", " ")
            for f in select_field_keys:
                select_dict[s] = select_dict[s].replace(f, select_fields[f])
        
        # print select_dict
        
        # Add extra role information on the returned query.
        qs = qs.extra(select = select_dict)
        return qs


    def get_query_set(self,):
        return self.duplicate_query_set().distinct()

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
    account_object = models.OneToOneField("Account", db_index = True, null = True, related_name = "+")
    is_community = models.BooleanField(default = False, db_index = True, )
    
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
    
    # The roles. It's strongly unrecommended to edit those roles by hand, use the 'permissions' property instead.
    _p_can_view = models.IntegerField(default = 15)
    _p_can_edit = models.IntegerField(default = 15)
    _p_can_list = models.IntegerField(default = 15)
    _p_can_list_members = models.IntegerField(default = 15)
    _p_can_publish = models.IntegerField(default = 15)
    _p_can_join = models.IntegerField(default = 15)
    _p_can_leave = models.IntegerField(default = 15)
    _p_can_create = models.IntegerField(default = 15)
    
    def get_absolute_url(self):
        """
        XXX TODO: Make this a little more MVC with @permalink decorator
        See http://docs.djangoproject.com/en/dev/ref/models/instances/#get-absolute-url
        XXX TODO: Don't use the 'object' accessor but use a twistable_category attribute in some way
        (eg. twistable_category is one of 'Account', 'Content', 'Menu' or 'Resource')
        """
        from twistranet.models import Content, Account, Community
        if isinstance(self.object, Content):
            return "/content/%i" % self.id
        elif isinstance(self.object, Community):
            return "/community/%i" % self.id
        elif isinstance(self.object, Account):
            return "/account/%i" % self.id
        raise NotImplementedError("Can't get absolute URL for object %s" % self)
            
    #                                                                   #
    #           Internal management, ensuring DB consistancy            #    
    #                                                                   #

    def save(self, *args, **kw):
        """
        Set various object attributes
        """
        import account, community
        self_owner = False
        self_publisher = False
        
        # Check if we're saving a real object and not a generic Content one (which is prohibited).
        # This must be a programming error, then.
        # XXX TODO: Check that type doesn't change. Also check that if id is None, type is None as well.
        if self.__class__.__name__ == Twistable.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
            
        # Set information used to retreive the actual subobject
        self.model_name = self._meta.object_name
        self.app_label = self._meta.app_label
        self.is_community = isinstance(self, community.Community)

        # Set owner & publisher upon object creation. Publisher is NEVER set as None by default.
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
    
        # Set permissions; we will apply them last to ensure we have an id
        if not self.permissions:
            perm_template = self.model_class.permission_templates
            if not perm_template:
                raise ValueError("permission_templates not defined on class %s" % self.__class__.__name__)
            self.permissions = perm_template.get_default()
        tpl = [ t for t in self.permission_templates.permissions() if t["id"] == self.permissions ]
        if not tpl:
            raise ValueError("Unable to find permission template %s in %s" % (self.permissions, self.permission_templates))
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
            
        # Self-pointer to the account object if this is an account (sorry, didn't find simpler method)
        ret = super(Twistable, self).save(*args, **kw)
        if creation and isinstance(self, account.Account):
            self.account_object = self
            super(Twistable, self).save()

        return ret
            
    @property
    def model_class(self):
        """
        Return the actual model's class.
        This method issues no DB query.
        XXX TODO: Cache this (not critical, though)
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
        return model.objects.get(id = self.id)
            
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
        MAX_HEADLINE_LENGTH = 140 - 5
        text = html.escape(text)
        if len(text) >= MAX_HEADLINE_LENGTH:
            text = u"%s [...]" % text[:MAX_HEADLINE_LENGTH]
        text = utils.escape_links(text)
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
    
