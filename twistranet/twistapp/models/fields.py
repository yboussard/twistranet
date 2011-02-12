"""
Twistranet Specific fields
"""
import os

from django import forms
from django.db import models
from django.core.validators import EMPTY_VALUES, RegexValidator
from django.utils.translation import ugettext as _

from  twistranet.twistapp.lib.log import log
from twistranet.twistapp.lib.slugify import FULL_SLUG_REGEX

class TwistableSlugField(models.SlugField):
    """
    A special case of a slug field, which handles slugs the way we want to handle them in TN:
    - slug is a regex
    - unicity checks
    """
    def __init__(self, *args, **kwargs):
        super(TwistableSlugField, self).__init__(*args, **kwargs)
        self.validators.append(RegexValidator(FULL_SLUG_REGEX))
    
class PermissionField(models.CharField):
    """
    A field used to store permission template value.
    It's a CharField with a special Choice() widget
    """
    max_length = 32
    
    def __init__(self, *args, **kw):
        """Enforce max_length"""
        kw['max_length'] = self.max_length
        super(PermissionField, self).__init__(*args, **kw)
        
    
    def formfield(self, **kwargs):
        from twistranet.twistapp.forms import fields
        defaults = {
            'form_class': fields.PermissionFormField,
            'choices': (),
        }
        defaults.update(kwargs)

        # return defaults
        return super(PermissionField, self).formfield(**defaults)


class ResourceField(models.ForeignKey):
    """
    ResourceField can be passed 2 arguments:
    - the resource id we're going to use (easy)
    - the File we're going to upload as a resource (more complicated)
    """
    def __init__(self, model = "Resource", allow_upload = True, allow_select = True, *args, **kw):
        """
        Default model is Resource.
        - model: The model to use as the Resource target. Use only a Resource-derived object.
        - allow_create: if False, won't allow to upload a new file.
        - allow_select: il False, won't allow to select a file from existing resources.
        """
        self.allow_upload = allow_upload
        self.allow_select = allow_select
        super(ResourceField, self).__init__(model, *args, **kw)
    
    def delete_file(self, instance, *args, **kwargs):
        if getattr(instance, self.attname):
            image = getattr(instance, '%s' % self.name)
            file_name = image.path
            # If the file exists and no other object of this type references it,
            # delete it from the filesystem.
            if os.path.exists(file_name) and \
                not instance.__class__._default_manager.filter(**{'%s__exact' % self.name: getattr(instance, self.attname)}).exclude(pk=instance._get_pk_val()):
                os.remove(file_name)

    def upload_resource(self, instance, data):
        """
        Upload the given file (data parameter) as a resource published by instance.
        Return the newly created resource object.
        """
        # Determine the new resource's publisher according to its type
        from twistranet.twistapp.models import Account, Resource, Content
        if isinstance(instance, Account):
            publisher = instance
        elif isinstance(instance, Content):
            publisher = instance.publisher
        else:
            raise NotImplementedError("Have to find who is the publisher for a new resource for %s" % (instance, ))
            
        # Create the resource itself
        resource = Resource(
            publisher = publisher,
            resource_file = data,
            )
        resource.save()
        return resource

    def get_internal_type(self):
        return 'ForeignKey'

    def save_form_data(self, instance, data):
        """
        If we're just given a reference, we set data accordingly.
        If we're given a file, we upload it and set data accordingly.
        If we're given both, we suppose the file must be uploaded.
        """
        from twistranet.twistapp.models import Resource
        resource = None
        
        # Process either upload file or resource id
        # XXX Fix me : i'm not sure
        if data:
            data_select, data_upload = data
            if self.allow_upload and data_upload:         # We have a file using a classic file field (no more used ?), it takes precedence.
                resource = self.upload_resource(instance, data_upload)
            elif (self.allow_upload or self.allow_select) and data_select:   # we have a dataselect using quickupload or browser select
                if isinstance(data_select, Resource):
                    resource = data_select
                elif isinstance(data_select, unicode):       # We just have an id. Try to get the resource.
                    resource = Resource.objects.get(id = data_select)
            else:
                raise ValueError("Invalid incoming data for resource field: %s" % data)

        # Supersave data
        super(ResourceField, self).save_form_data(instance, resource)

    def formfield(self, **kwargs):
        from twistranet.twistapp.forms import fields
        defaults = {
            'form_class': fields.ResourceFormField,
            'allow_upload': self.allow_upload,
            'allow_select': self.allow_select,
        }
        defaults.update(kwargs)
        return super(ResourceField, self).formfield(**defaults)

