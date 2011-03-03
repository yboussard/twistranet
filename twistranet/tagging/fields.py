"""
Tagging fields.
These are only form fields.
"""
import os
from django import forms
from django.db import models
from django.core.validators import EMPTY_VALUES
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.validators import EMPTY_VALUES
from django.utils.encoding import smart_unicode, force_unicode

import widgets

class TagsFormField(forms.ModelMultipleChoiceField):
    """
    This overrides the regular ChoiceField to add additional rendering.
    """
    widget = widgets.TagsWidget()
    
    # this method will be used to create object labels by the QuerySetIterator.
    # Override it to customize the label.
    def label_from_instance(self, obj):
        """
        This method is used to convert objects into strings; it's used to
        generate the labels for the choices presented by this object. Subclasses
        can override this method to customize the display of the choices.
        """
        return smart_unicode(obj.title_or_description)

    def clean(self, value):
        """
        Here we just scan values to de-reference them properly,
        and create additional tags if necessary.
        """
        # This is from ModelMultipleChoiceField.clean()
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['list'])
                
        # Here's where the work begins. We isolate unexisting tags.
        only_ids = []
        for v in value:
            try:
                only_ids.append(int(v))
            except:
                pass
        qs = self.queryset.filter(pk__in = only_ids)
        pks = set([force_unicode(o.pk) for o in qs])
        new_value = []
        for val in value:
            if force_unicode(val) in pks:
                new_value.append(val)
            else:
                # Try to find a stripped version.
                vq = self.queryset.filter(title__icontains = val.strip())
                if vq:
                    new_value.append(force_unicode(vq[0].pk))
                elif "CAN_CREATE_NEW_TAGS":
                    # XXX POSSIBLY TODO: Here we could check if tag creation is authorized or not.
                    new_tag = self.queryset.create(title = val.strip())
                    new_value.append(force_unicode(new_tag.pk))
                else:
                    raise ValidationError(self.error_messages['invalid_choice'] % val)
        return self.queryset.filter(pk__in = new_value)
