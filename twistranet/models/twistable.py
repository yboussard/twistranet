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
    XXX TODO: Make resource inherit from that too?
    XXX TODO: Securise the base manager!
    """
    objects = _basemanager.BaseManager()

    slug = models.SlugField(unique = True, db_index = True, null = True)                 # XXX TODO: Have a more personalized slug field (allowing dots for usernames?)
    object_type = models.CharField(max_length = 64, db_index = True)

    language = models.CharField(
        max_length = 10,
        blank = True,
        choices = languages.available_languages,
        default = languages.available_languages[0][0],
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
        # Check if we're saving a real object and not a generic Content one (which is prohibited).
        # This must be a programming error, then.
        # XXX TODO: Check that type doesn't change. Also check that if id is None, type is None as well.
        if self.__class__.__name__ == Twistable.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
        self.object_type = self.__class__.__name__
        return super(Twistable, self).save(*args, **kw)
            
    @property
    def object(self):
        """
        Return the exact subclass this object belongs to.
        XXX TODO: Implement inheritance here correctly
        """
        if self.id is None:
            raise RuntimeError("You can't get subclass until your object is saved in database.")
        type_field = self.object_type.lower()
        type_field_id = "%s_id" % type_field
            
        # XXX Ultra ugly but temporary until I find a way to implement inheritance here
        # Direct types (Resource, MenuItem, ...)
        try:                        return getattr(self, type_field)
        except AttributeError:      pass

        # 1st level inheritance
        for first_level in ('content', 'account', 'resource', 'menuitem'):
            try:                            obj1 = getattr(self, first_level)
            except ObjectDoesNotExist:      continue
            try:                            return getattr(obj1, type_field)
            except AttributeError:          pass
            
            # 2nd level inheritance
            for second_level in ('community', ):
                try:                        obj2 = getattr(obj1, second_level)
                except ObjectDoesNotExist:  continue
                return getattr(obj2, type_field)

        # Arf, didn't find.
        raise AttributeError("Unable ot find object for %s:%s:%s:%s %s" % (self, self.object_type, self.id, self.slug, dir(self) ))
            
    class Meta:
        app_label = "twistranet"

    #                                                                   #
    #                       Security Management                         #
    # XXX TODO: Use a more generic approach? And some caching as well?  #
    # XXX Also, must check that permissions are valid for the given obj #
    #                                                                   #

    @property
    def can_list(self):
        """
        Same as can_view for content objects?
        XXX TODO: Clean that a little bit?
        """
        
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_view, self)

    @property
    def can_view(self):
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_view, self)

    @property
    def can_delete(self):
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_delete, self)

    @property
    def can_edit(self):
        auth = Twistable.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_edit, self)


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
            
    
