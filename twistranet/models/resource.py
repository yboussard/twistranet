import os

from django.db import models
from django.db.models import Q, FileField
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation

from twistorage.storage import Twistorage
from twistranet.lib import languages, permissions
import twistable


def twistorage_upload_to(instance, filename):
    """
    Upload to the instance's publisher's account.
    """
    if not instance.publisher:
        raise ValueError("Can't upload a file before a publisher is set on the resource.")
    if not instance.publisher.can_edit:
        raise PermissionDenied("You're not allowed to upload a file on '%s'." % instance.publisher)
    if instance.publisher.slug:
        return os.path.join(instance.publisher.slug, filename)
    return os.path.join(str(instance.publisher.id), filename)

class Resource(twistable.Twistable):
    """
    A resource object.
    See doc/DESIGN.txt for design considerations
    
    XXX TODO: Implement URL resources.
    """
    # Special manager for resources
    # objects = ResourceModelManager()
    
    # Resource actual information.
    resource_file = FileField(upload_to = twistorage_upload_to, storage = Twistorage())
    resource_url = models.URLField(max_length = 1024, null = True)                  # Original URL if given
    
    # Title / Description are optional resource description information.
    # May be given by the manager, BUT will be stored in TN.
    # mimetype = models.CharField(max_length = 64)
    # encoding = models.CharField(max_length = 64, null = True)

    # Resource securization
    permission_templates = permissions.content_templates        # This is the lazy man's solution, we use same perms as content ;)

    class Meta:
        app_label = 'twistranet'
    
    