from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

from resourcemanager import ResourceManager
import basemanager 

class ResourceObjectsManager(basemanager.BaseManager):
    """
    XXX TODO: Securize resource access
    """
    def get_query_set(self,):
        """
        Resources are either bound (to a content) or not.
        An unbound resource has the scope of its owner account.
        A bound resource has the scope of all its related content (the most "opened" one).
        """
        from content import Content
        from account import Account
        authenticated = self._getAuthenticatedAccount()
        return super(ResourceObjectsManager, self).get_query_set().filter(
            (
                # Bound content
                Q(bound = True, content__in = Content.objects.get_query_set())
                ) | (
                # Unbound content
                Q(bound = False, owner__in = Account.objects.get_query_set())
                ) | (
                # Content I own (just to be sure)
                Q(owner = authenticated)
                )
            ).distinct()
        
    

class Resource(models.Model):
    """
    A resource object.
    See doc/DESIGN.txt for design considerations
    """
    # Resource location descriptors.
    # Locator is a (possibly looong) string used by the manager to find the resource
    manager = models.ForeignKey(ResourceManager)
    locator = models.CharField(max_length = 1024)
    alias = models.CharField(max_length = 1024, unique = True, null = True)  # An optional alias to get the resource
    
    # Title / Description are optional resource description information.
    # May be given by the manager, BUT will be stored in TN.
    title = models.CharField(max_length = 255)
    description = models.TextField()
    mimetype = models.CharField(max_length = 64)
    encoding = models.CharField(max_length = 64, null = True)

    # Resource owner and securization
    bound = models.BooleanField(default = False)
    owner = models.ForeignKey("Account", related_name = "owned_resources")
    objects = ResourceObjectsManager()

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
        if self.owner_id is None:
            self.owner = authenticated
        else:
            if self.owner != authenticated:
                if not self.owner.is_admin:
                    raise RuntimeError("You're not allowed to edit this resource. XXX TODO: Resource delegation?")

        # Actually save it
        return super(Resource, self).save(*args, **kw)


    def get(self):
        """
        Return a stream pointing to this resource's raw content
        """
        return self.manager.subclass.readResource(self)
    
    
    