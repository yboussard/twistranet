"""
Base of the securable (ie. directly accessible through the web), translatable and full-featured TN object.

A twist-able object in TN is an object which can be accessed safely from a view.
Normally, everything a view manipulates must be taken from a TN object.

Content, Accounts, MenuItems, ... are all Twistable objects.

This abstract class provides a lot of little tricks to handle view/model articulation,
such as the slug management, prepares translation management and so on.
"""

from django.db import models
from django.db.models import Q
from django.db.models import loading
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.utils import html, translation
from twistranet.lib import roles, permissions, languages, utils
from twistranet.models import _basemanager

class Twistable(models.Model):
    """
    Base (an abstract) type for rich, inheritable and securable TN objects.
    
    This class is quite optimal when using its base methods but you should always use
    your dereferenced class when you can do so!
    
    All Content and Account classes derive from this.
    XXX TODO: Securise the base manager!
    """
    objects = _basemanager.BaseManager()

    # Object management. Slug is optional (id is not ;))
    slug = models.SlugField(unique = True, db_index = True, null = True)                 # XXX TODO: Have a more personalized slug field (allowing dots for usernames?)
    
    # This is a way to de-reference the underlying model rapidly
    app_label = models.CharField(max_length = 64, db_index = True)
    model_name = models.CharField(max_length = 64, db_index = True)

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
    
    # Our security model.
    # XXX TODO: Use a foreign key instead with some clever checking? Or a specific PermissionField?
    # XXX because there's a problem here as choices cannot be re-defined for subclasses.
    permission_templates = ()       # Define this in your subclasses
    permissions = models.CharField(
        max_length = 32,
        db_index = True,
    )
    
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
        import _permissionmapping
        
        # Check if we're saving a real object and not a generic Content one (which is prohibited).
        # This must be a programming error, then.
        # XXX TODO: Check that type doesn't change. Also check that if id is None, type is None as well.
        if self.__class__.__name__ == Twistable.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
            
        # Set information used to retreive the actual subobject
        self.model_name = self._meta.object_name
        self.app_label = self._meta.app_label
        
        # Set permissions; we will apply them last to ensure we have an id
        if not self.permissions:
            perm_template = self.model_class.permission_templates
            if perm_template:
                self.permissions = perm_template.get_default()
        
        ret = super(Twistable, self).save(*args, **kw)

        # Set/reset permissions. We do it last to ensure we have an id. Ignore AttributeError from object pty
        if self.permissions:
            _permissionmapping._PermissionMapping.objects._applyPermissionsTemplate(self)
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

        # Get model class, then walk through ancestors
        # XXX I can cache MRO resolution, I guess, though it might not be very expensive
        model = loading.get_model(self.app_label, self.model_name)
        if isinstance(self, model):
            return self
        return model.objects.get(id = self.id)
        
        # XXX I keep the following code under my pillow. Looks like it's not efficient enough (yet!)
        # model_mro = list(model.__mro__)
        # model_mro.reverse()
        # obj = None
        # for base_cls in model_mro:
        #     # Don't do anything until we find the Twistable class.
        #     if not obj:
        #         if issubclass(base_cls, Twistable):
        #             obj = self
        #         continue
        #     
        #     # Here isinstance() is ok as we have 'older' ancestors first.
        #     if issubclass(base_cls, Twistable):
        #         if base_cls._meta.abstract:
        #             continue
        #         ancestor_fied = base_cls._meta.object_name.lower()
        #         obj = getattr(obj, ancestor_fied)
        #
        # return obj
            
    class Meta:
        app_label = "twistranet"

    #                                                                   #
    #                       Security Management                         #
    # XXX TODO: Use a more generic approach? And some caching as well?  #
    # XXX Also, must check that permissions are valid for the given obj #
    #                                                                   #

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
        return _TranslationWrapper(self, language)
            
    
