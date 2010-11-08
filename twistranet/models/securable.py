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

    class Meta:
        abstract = True

