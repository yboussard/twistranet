import mimetypes

from django.db import models, IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import HttpResponse

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
            # Maybe that's just a matter of checking the can_edit permission on an account?
            # raise RuntimeError("Unauthorized method. Must be called from the System Account only.")
            pass
        
        # Save manager_type info
        self.manager_type = self.__class__.__name__
        if self.manager_type == ResourceManager.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
            
        # Super-save
        super(ResourceManager, self).save(*args, **kw)

    class Meta:
        app_label = 'twistranet'
        
class _AbstractFilesystemResourceManager(ResourceManager):
    # Default value is TN's default resources path
    path = models.CharField(max_length = 512, default = settings.TWISTRANET_DEFAULT_RESOURCES_DIR)
    
    class Meta:
        abstract = True
        app_label = 'twistranet'

    def saveResource(self, resource, uploaded):
        """
        Save a resource from the given uploaded file
        """
        raise NotImplementedError("You can't save a file on a readonly manager.")

    def readResource(self, resource, ):
        """
        Return a pointer to the given resource FILE. Use this in a view.
        """
        # Security check against locator path (avoid "/../../" hacks)
        filename = resource.locator
        fpath = os.path.abspath(os.path.join(self.path, filename))
        if not fpath.startswith(os.path.abspath(self.path)):
            raise ValueError("Invalid locator path: %s" % fpath)

        # Open file descriptor
        f = open(fpath, "rb").read()
        content_type = mimetypes.guess_type(filename)[0]
        return HttpResponse(f, mimetype=content_type)

class ReadOnlyFilesystemResourceManager(_AbstractFilesystemResourceManager):
    """
    A readonly FS manager.
    It is used for legacy TN resource (profile images, ...)

    Locator is a filepath below the 'path' value.
    """

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
                    r.original_filename = fname
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
    

class FileSystemResourceManager(_AbstractFilesystemResourceManager):
    """
    A R/W FS resource manager. Must be attached to an account.
    This is how media is managed on a per-account basis.
    
    'path' is not settable, it's given a value relative to TWISTRANET_ACCOUNT_MEDIA_PATH directory.
    """
    account = models.OneToOneField('Account', related_name = '_media_resource_manager', )
    _root_path = settings.TWISTRANET_ACCOUNT_MEDIA_PATH
    
    class Meta:
        app_label = 'twistranet'
        
    def uploadResource(self, uploaded):
        """
        Create a resource based on the given upload file and attached to the current account.
        Return the created resource.
        """
        from twistranet.models.resource import Resource
        from twistranet.models.account import Account
        resource = Resource(
            owner = Account.objects._getAuthenticatedAccount(),
            manager = self,
        )
        self.saveResource(resource, uploaded)
        print "Saved resource", resource, resource.id
        return resource

    def saveResource(self, resource, uploaded):
        """
        Save the given uploaded file.
        uploaded must be an UploadedFile object.
        Will erase any content that's already there.
        The resource object will be save if it doesn't have an id!
        """
        # Set resource manager if not set
        if not resource.manager:
            resource.manager = self
        else:
            NotImplementedError("Should raise a permission error if we try to switch managers")
        
        # Save resource so that we have an id
        if not resource.id:
            resource.save()
        filename = os.path.join(self.path, "%s" % resource.id)
        
        # Write the file
        destination = open(filename, 'wb+')
        for chunk in uploaded.chunks():
            destination.write(chunk)
        destination.close()
        
        # Set resource properties
        # XXX TODO: Maybe we could use the 'magic' module?
        # Set pties and save
        resource.locator = "%s" % (resource.id, )
        resource.original_filename = uploaded.name
        resource.mimetype = uploaded.content_type
        resource.encoding = uploaded.charset            # XXX TODO: Handle encoding...
        resource.save()

    def save(self, *args, **kw):
        """
        Handle particular attributes
        """
        # Create the path according to where this FSRM is supposed to be
        self.path = os.path.join(self._root_path, "%s" % self.account_id)
        if os.path.exists(self.path):
            ### XXX TODO: check if directory is empty to avoid nameclash
            pass
            # raise ValueError("FileSystemResourceManager can't create path %s: already exists. Please save your files and remove this directory." % self.path)
        else:
            os.makedirs(self.path)
        
        # Superclass save
        super(FileSystemResourceManager, self).save(*args, **kw)



