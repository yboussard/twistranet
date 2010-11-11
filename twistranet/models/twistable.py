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
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import html, translation
from twistranet.lib import roles, permissions, languages, utils

class Twistable(models.Model):
    """
    Base (an abstract) type for rich, inheritable and securable TN objects.
    
    All Content and Account classes derive from this.
    XXX TODO: Make resource inherit from that too?
    """
    slug = models.SlugField(unique = True, db_index = True, null = True)                 # XXX TODO: Have a more personalized slug field (allowing dots for usernames?)
    object_type = models.CharField(max_length = 64, db_index = True)
    
    def get_absolute_url(self):
        """
        XXX TODO: Make this a little more MVC with @permalink decorator
        See http://docs.djangoproject.com/en/dev/ref/models/instances/#get-absolute-url
        """
        from twistranet.models import Content, Account, Community
        if isinstance(self, Content):
            return "/content/%i" % self.id
        elif isinstance(self, Community):
            return "/community/%i" % self.id
        elif isinstance(self, Account):
            return "/account/%i" % self.id
        raise NotImplementedError("Can't get absolute URL for object %s" % self)
            
    @property
    def object(self):
        """
        Return the exact subclass this object belongs to.
        """
        if self.id is None:
            raise RuntimeError("You can't get subclass until your object is saved in database.")
        return getattr(self, self.object_type.lower())
            
            
    class Meta:
        app_label = "twistranet"

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
            
    
