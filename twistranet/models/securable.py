"""
Base of the securable (ie. directly accessible through the web)

This abstract class provides a lot of little tricks to handle view/model articulation,
such as the slug management.
"""

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import html
from twistranet.lib import roles, permissions, languages, utils

class Securable(models.Model):
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
            
    class Meta:
        abstract = True

