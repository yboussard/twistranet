"""
The twistranet Resource Field.
Used to manage resource upload.
"""
import os

from django import forms
from django.db import models
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext as _

import widgets

class ModelInputField(forms.Field):
    """
    This is a field used to enter a foreign key value inside a classic Input widget.
    This is used when there are a lot of values to check against (and ModelChoiceField is not
    efficient anymore), plus the value is checked against the QuerySet very late in the process.
    """

    def __init__(
        self, model, filter = None, required=True, widget=None, 
        label=None, initial=None, help_text=None, to_field_name=None, 
        *args, **kwargs
        ):
        super(ModelInputField, self).__init__(required, widget, label, initial, help_text,
                       *args, **kwargs)
        self.model = model
        self.filter = filter
        self.to_field_name = to_field_name
        
        # We put this here to avoid import errors
        self.default_error_messages = {
            'invalid_choice': _(u'Select a valid choice. That choice is not one of'
                                u' the available choices.'),
        }
    
    def to_python(self, value):
        """
        'Resolve' the query set at validation time.
        This way, we're sure to have the freshest version of the QS.
        """
        if value in EMPTY_VALUES:
            return None
        try:
            key = self.to_field_name or 'pk'
            qs = self.model.objects.get_query_set()
            if self.filter:
                qs = qs.filter(self.filter)
            value = qs.get(**{key: value})
        except self.queryset.model.DoesNotExist:
            raise ValidationError(self.error_messages['invalid_choice'])
        return value
    

class ResourceFormField(forms.MultiValueField):
    """
    The ResourceFormField is a resource browser.
    You can pass it a few parameters:
    - model which is the subclass you want to read your resources from (default: twistranet.Resource).
        Useful if you want to display only images for example.
    - filter which will be passed to model.objects.filter() call before rendering the widget.
        These model / filter params are the only solution to handle choices WITH the security model.
    """
    widget = widgets.ResourceWidget
    field = ModelInputField
    model = None
    filter = None

    def __init__(self, *args, **kwargs):
        # Initial values
        from twistranet.models import Resource
        self.model = kwargs.pop("model", Resource)
        self.filter = kwargs.pop("filter", None)
        self.widget = kwargs.pop("widget", self.widget(model = self.model, filter = self.filter))
        self.required = kwargs.pop("required", True)
        
        # The fields we'll use:
        # - A ModelInputField used to handle the ForeignKey.
        # - A FileField used to handle data upload.
        field0 = self.field(model = self.model, filter = self.filter, required = self.required)
        field1 = forms.FileField(required = False)
        fields = [ field0, field1, ]
        
        # # Compatibility with form_for_instance
        # if kwargs.get('initial'):
        #     initial = kwargs['initial']
        # else:
        #     initial = None
        # self.widget = self.widget(initial=initial)

        super(ResourceFormField, self).__init__(fields, label = kwargs.pop('label'), required = False)  #self.required)
        
    def prepare_value(self, value):
        """
        Pass the query_set to the underlying widget, so that it's computed as late as possible.
        """
        qs = self.model.objects.get_query_set()
        if self.filter:
            qs = qs.filter(self.filter)
        self.widget.query_set = qs
        return super(ResourceFormField, self).prepare_value(value)
        
    def compress(self, data_list):
        return data_list


class ResourceField(models.ForeignKey):
    """
    ResourceField can be passed 2 arguments:
    - the resource id we're going to use (easy)
    - the File we're going to upload as a resource (more complicated)
    """
    
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
        from twistranet.models import Account, Resource
        if isinstance(instance, Account):
            publisher = instance
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
        from twistranet.models import Resource
        resource = None
        
        # Process either upload file or resource id
        if data:
            if data[1]:         # We have a file, it takes precedence.
                resource = self.upload_resource(instance, data[1])
            elif data[0] and isinstance(data[0], int):       # We just have an id. Try to get the resource.
                resource = Resource.objects.get(id = data[0])
            elif data[0] and isinstance(data[0], Resource):
                resource = data[0]
            else:
                raise ValueError("Invalid incoming data for resource field: %s" % data)
            
        super(ResourceField, self).save_form_data(instance, resource)

    def formfield(self, **kwargs):
        defaults = {'form_class': ResourceFormField}
        defaults.update(kwargs)
        return super(ResourceField, self).formfield(**defaults)






