import os
import mimetypes
from django.db import models
from django.db.models import Q, FileField
from django.core.exceptions import ObjectDoesNotExist, ValidationError, PermissionDenied, SuspiciousOperation

from twistranet.twistorage.storage import Twistorage
from twistranet.twistapp.lib import languages, permissions
from  twistranet.twistapp.lib.log import *
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
        
        act_accounts = []
        for a in accounts:
            if self.filter(publisher__id = a.id):
                act_accounts.append(a)
        return act_accounts

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
    filename = models.CharField(max_length = 255, blank = True)     # http://en.wikipedia.org/wiki/Comparison_of_file_systems
    mimetype = models.CharField(max_length = 64)
    encoding = models.CharField(max_length = 64, blank = True)

    # Resource securization
    permission_templates = permissions.content_templates        # This is the lazy man's solution, we use same perms as content ;)
    
    # General information
    default_picture_resource_slug = "default_resource_picture"

    class Meta:
        app_label = 'twistapp'

    def save(self, *args, **kw):
        """
        Properly set title if not set.
        """
        if not self.title:
            if self.resource_file:
                self.title = self._pretty_title(self.resource_file.name)
        self.mimetype = self.content_type
        return super(Resource, self).save(*args, **kw)
        
    def _pretty_title(self, raw_filename):
        """XXX TODO: transform raw filename into a pretty title
        """
        return raw_filename
        
    @property
    def is_image(self,):
        """True if this is an image.
        """
        return self.mimetype.startswith("image/")
        
    # @property
    # def filename(self,):
    #     """Return the underlying filename
    #     """
    #     if self.resource_file:
    #         name = getattr(self.resource_file, 'name', '')
    #         name = os.path.split(name)[1]
    #         return name
        
    @property
    def image(self,):
        """
        Return the attribute suitable for sorl-thumbnail.
        """
        if self.resource_file:
            if self.is_image:
                return self.resource_file
            else:
                return self.mimetype_icon

        if self.resource_url:
            return self.mimetype_icon

    @property
    def mimetype_icon(self):
        mimetype_slug = self.mimetype.replace('/','_')
        try:
            src = Resource.objects.get(slug = mimetype_slug)
        except:
            src = Resource.objects.get(slug = self.default_picture_resource_slug)
        return src.image

    @property
    def content_type(self,):
        if self.resource_file:
            name = getattr(self.resource_file, 'name', '')
            ct = mimetypes.guess_type(name)[0] or 'application/octet-stream'
        if self.resource_url:
            name = self.resource_url.split('/')[-1]
            # TODO > more complex stuff here to get default 
            # mimetype
            default_mimetype = 'text/html'
            ct = mimetypes.guess_type(name)[0] or default_mimetype
        return ct


# class ImageResource(Resource):
#     """
#     An ImageResource if a File with dedicated Image features.
#     It's used for the picture attribute of all Twistable objects.
#     """    
#     def save(self, *args, **kw):
#         """
#         While computing content_type, we double-check that it's an image.
#         """
#         ct = self.content_type
#         if not ct.startswith("image/"):
#             raise ValueError("Invalid MIME type for %s: %s" % (self, ct))
#         return super(ImageResource, self).save(*args, **kw)
# 
#     class Meta:
#         app_label = 'twistapp'



