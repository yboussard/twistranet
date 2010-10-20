import mimetypes

from django.db import models, IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist

import os
import os.path
import settings

class ResourceManager(models.Model):
    """
    A resource manager descriptor.
    See doc/DESIGN.txt for design considerations.
    
    This is not an abstract class but must be subclassed.
    """
    # Main fields
    name = models.CharField(max_length = 64, unique = True)        # A friendly ressource manager name
    manager_type = models.CharField(max_length = 64)
    
    EDITABLE = False    # Put this to True if you want to allow file upload/edition
                        # Note that resource metadata will still be modifiable (because stored in DB),
                        # at least for managers storing metadata.
                        
    def readResource(self, resource):
        """
        Return a stream for the given resource. Will use the 'locator' to find it.
        """
        raise NotImplementedError("You must subclass the ResourceManager.readResource() in your Resource Manager.")

    @property
    def subclass(self):
        """
        Return the exact subclass this object belongs to.
        Use this to access the actual manager.
        """
        # XXX TODO: Check against errors
        obj = getattr(self, self.manager_type.lower())
        return obj
    
    
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        # Avoid creation by non-admin
        from resource import Resource
        authenticated = Resource.objects._getAuthenticatedAccount()
        if not authenticated.account_type == "SystemAccount":
            # XXX TODO: Non-admin check ;)
            raise RuntimeError("Unauthorized method. Must be called from the System Account only.")
        
        # Save manager_type info
        self.manager_type = self.__class__.__name__
        if self.manager_type == ResourceManager.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
            
        # Super-save
        super(ResourceManager, self).save(*args, **kw)

    class Meta:
        app_label = 'twistranet'
    

class ReadOnlyFilesystemResourceManager(ResourceManager):
    """
    A readonly FS manager.
    It is used for legacy TN resource (profile images, ...)
    
    Locator is a filepath below the 'path' value.
    """
    # Default value is TN's default resources path
    path = models.CharField(max_length = 512, default = settings.TWISTRANET_DEFAULT_RESOURCES_DIR)

    class Meta:
        app_label = 'twistranet'
        
    def loadAll(self, with_aliases = False):
        """
        Special method to load all the filesystem content and transform each file into a file resource.
        Must be called from a SystemAccount for security reasons, all generated resources will belong to SystemAccount.
        """
        # Security check
        from resource import Resource
        authenticated = Resource.objects._getAuthenticatedAccount()
        if not authenticated.account_type == "SystemAccount":
            raise RuntimeError("Unauthorized method. Must be called from the System Account only.")
        
        # Load each file, avoiding to replace it
        for root, dirs, files in os.walk(self.path):
            for fname in files:
                # By now, we ignore None mimetypes (we don't know how to handle 'em)
                # XXX TODO: Check if file and dir objects are processed normally!
                mimetype, encoding = mimetypes.guess_type(fname)
                defaults = {
                    "mimetype": mimetype,
                    "encoding": encoding,
                }
                if not mimetype:
                    continue
                if with_aliases:
                    alias = os.path.splitext(os.path.split(fname)[1])[0]
                    defaults['alias'] = alias
                    objects = Resource.objects.filter(
                        manager = self, 
                        alias = alias,
                        )
                    if objects:
                        if len(objects) > 1:
                            raise IntegrityError("More than one resource with '%s' alias" % alias)
                        r = objects[0]
                    else:
                        r = Resource()
                    
                    # Set pties and save
                    r.manager = self
                    r.locator = fname
                    r.alias = alias
                    r.mimetype = mimetype
                    r.encoding = encoding
                    r.save()
                else:
                    raise NotImplementedError("Should implement w/o aliases")
                    Resource.objects.get_or_create(
                        manager = self, 
                        locator = fname,
                        defaults = defaults,
                    )
    
    def readResource(self, resource):
        """
        Return a pointer to the given resource file.
        """
        # Security check against locator path (avoid "/../../" hacks)
        fpath = os.path.abspath(os.path.join(self.path, resource.locator))
        if not fpath.startswith(os.path.abspath(self.path)):
            raise ValueError("Invalid locator path: %s" % fpath)
        
        # Open file descriptor
        f = open(fpath, "r")
        return f



