"""
The twistranet Resource Field.
Used to manage resource upload.
"""
import os
from django import forms
from django.db import models
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext as _
from  twistranet.twistranet.lib.log import log
import widgets

class PermissionFormField(forms.ChoiceField):
    """
    This overrides the regular ChoiceField to add additional rendering.
    """
    widget = widgets.PermissionsWidget

    def __init__(
        self, choices = (), required=True, widget=None, max_length = None,
        label=None, initial=None, help_text=None, to_field_name=None, 
        *args, **kwargs
        ):
        super(PermissionFormField, self).__init__(choices, required, widget, label, initial, help_text, *args, **kwargs)
        
        # We put this here to avoid import errors
        self.default_error_messages = {
            'invalid_choice': _(u'Select a valid choice. That choice is not one of'
                                u' the available choices.'),
        }

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
    - allow_upload (upload is ok)
    - allow_select (can select an existing resource from the given filter)
    """
    widget = widgets.ResourceWidget
    field = ModelInputField
    model = None
    filter = None

    def __init__(self, *args, **kwargs):
        # Initial values
        from twistranet.twistranet.models import Resource
        self.model = kwargs.pop("model", Resource)
        self.filter = kwargs.pop("filter", None)
        self.allow_upload = kwargs.pop("allow_upload", True)
        self.allow_select = kwargs.pop("allow_select", True)
        self.widget = kwargs.pop("widget", self.widget(
            model = self.model, filter = self.filter,
            allow_upload = self.allow_upload,
            allow_select = self.allow_select,
        ))
        self.required = kwargs.pop("required", True)
        
        # The fields we'll use:
        # - A ModelInputField used to handle the ForeignKey.
        # - A FileField used to handle data upload.
        fields = []
        field0 = self.field(model = self.model, filter = self.filter, required = self.required)
        field1 = forms.FileField(required = False)
        dummy = forms.CharField(required = False)
        if self.allow_select:
            fields.append(field0)
        else:
            fields.append(dummy)
        if self.allow_upload:
            fields.append(field1)
        else:
            fields.append(dummy)
        
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

