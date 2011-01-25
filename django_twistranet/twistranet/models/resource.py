import os

from django.db import models
from django.db.models import Q, FileField
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation

from django_twistranet.twistorage.storage import Twistorage
from django_twistranet.twistranet.lib import languages, permissions
from  django_twistranet.twistranet.lib.log import *
import twistable

class ResourceModelManager(twistable.TwistableManager):
    """
    We just add a few method to fetch resource-specific objects.
    """
    def selectable_accounts(self, account):
        """
        We just return current account (if not anon.) PLUS all the communities I rule.
        This is to fetch resources from specific accounts / communities.
        This is especially used in the Resource Selection Widget.
        Anonymous have no accounts to select things from.
        """
        if account.is_anonymous:
            return []
        accounts = [account]
        accounts.extend(account.communities.all())
        return accounts

def twistorage_upload_to(instance, filename):
    """
    Upload to the instance's publisher's account.
    """
    if not instance.publisher:
        raise ValueError("Can't upload a file before a publisher is set on the resource.")
    if not instance.publisher.can_edit:
        raise PermissionDenied("You're not allowed to upload a file on '%s'." % instance.publisher)
    return os.path.join(str(instance.publisher.id), filename)

class Resource(twistable.Twistable):
    """
    A resource object.
    See doc/DESIGN.txt for design considerations.
    
    XXX TODO: Implement URL resources.
    """
    # Special manager for resources
    objects = ResourceModelManager()
    
    # Resource actual information.
    resource_file = FileField(upload_to = twistorage_upload_to, storage = Twistorage(), null = True)
    resource_url = models.URLField(max_length = 1024, null = True, blank = True)                  # Original URL if given
    
    # Title / Description are optional resource description information.
    # May be given by the manager, BUT will be stored in TN.
    # mimetype = models.CharField(max_length = 64)
    # encoding = models.CharField(max_length = 64, null = True)

    # Resource securization
    permission_templates = permissions.content_templates        # This is the lazy man's solution, we use same perms as content ;)
    
    # General information
    default_picture_resource_slug = "default_resource_picture"

    class Meta:
        app_label = 'twistranet'

    def save(self, *args, **kw):
        """
        Properly set title if not set.
        """
        if not self.title:
            if self.resource_file:
                self.title = self.resource_file.name
        return super(Resource, self).save(*args, **kw)
        
    @property
    def image(self,):
        """
        Return the attribute suitable for sorl-thumbnail.
        """
        if self.resource_file:
            return self.resource_file
        if self.resource_url:
            return self.resource_url
    
    
    