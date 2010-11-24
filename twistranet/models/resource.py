from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from resourcemanager import ResourceManager
from twistranet.lib import languages, permissions
import twistable

# Web-compliant image formats
IMAGE_MIMETYPES = [
    "image/png",
    "image/jpeg",
    "image/gif",
    ]

class ResourceModelManager(twistable.TwistableManager):
    """
    A resource-specific manager with some additional media features
    """
    def query_images(self,):
        """
        Return images MIME types
        """
        return self.get_query_set().filter(mimetype__in = IMAGE_MIMETYPES)

class Resource(twistable.Twistable):
    """
    A resource object.
    See doc/DESIGN.txt for design considerations
    """
    # Special manager for resources
    objects = ResourceModelManager()
    
    # Resource location descriptors.
    # Locator is a (possibly looong) string used by the manager to find the resource
    manager = models.ForeignKey(ResourceManager, null = True, blank = True)         # If None, then the resource is DB-only. Field name is given by the accessor attribute.
    locator = models.CharField(max_length = 1024, unique = True)
    md5 = models.CharField(max_length = 32, unique = False)
    original_filename = models.CharField(max_length = 1024, null = True)            # Original filename if given
    original_url = models.URLField(max_length = 1024, null = True)                  # Original URL if given
    
    # Title / Description are optional resource description information.
    # May be given by the manager, BUT will be stored in TN.
    mimetype = models.CharField(max_length = 64)
    encoding = models.CharField(max_length = 64, null = True)

    # Resource owner and securization
    # bound = models.BooleanField(default = False)
    # objects = ResourceObjectsManager()
    permission_templates = permissions.content_templates        # This is the lazy man's solution, we use same perms as content ;)

    def __unicode__(self):
        return "%s:%s" % (self.manager, self.locator)

    class Meta:
        app_label = 'twistranet'
        
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        # Check content edition
        authenticated = Resource.objects._getAuthenticatedAccount()
        if not authenticated:
            raise ValidationError("You can't save a resource anonymously.")
                
        # Actually save it
        return super(Resource, self).save(*args, **kw)

    def get(self):
        """
        Return a stream pointing to this resource's raw content
        """
        if self.manager:
            return self.manager.subclass.readResource(self)
        else:
            return getattr(self.object, self.locator)
    
    
    