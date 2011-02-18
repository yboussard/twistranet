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
    ResourceField can be passed 1 argument:
    - the resource id we're going to use
    """
    def __init__(self, model = "Resource", allow_upload = True, allow_select = True, media_type='file', *args, **kw):
        """
        Default model is Resource.
        - model: The model to use as the Resource target. Use only a Resource-derived object.
        - allow_select: if False, won't allow to select a file from existing resources.
        - allow_upload: if False, won't display the widget to upload resource before select.
        - media_type: if set to 'image' allow only upload or select images mimetype, 
                      could be also 'flash', 'video', or string list of extensions '*.doc;*.pdf'.
        """
        self.allow_upload = allow_upload
        self.allow_select = allow_select
        self.media_type = media_type
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
        if data:
            data_select = data[0]
            if isinstance(data_select, Resource):
                resource = data_select
            elif isinstance(data_select, unicode):       # We just have an id. Try to get the resource.
                try :
                    resource = Resource.objects.get(id = data_select)
                except:
                    raise ValueError("Resource not found : %s" % data_select)
            else:
                raise ValueError("Invalid incoming data type for resource field: %s" % data[0])

        # Supersave data
        super(ResourceField, self).save_form_data(instance, resource)

    def formfield(self, **kwargs):
        from twistranet.twistapp.forms import fields
        defaults = {
            'form_class': fields.ResourceFormField,
            'allow_upload': self.allow_upload,
            'allow_select': self.allow_select, 
            'media_type': self.media_type,
        }
        defaults.update(kwargs)
        return super(ResourceField, self).formfield(**defaults)

