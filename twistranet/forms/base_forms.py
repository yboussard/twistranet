from django import forms
from django.db import models
from django.forms import widgets


class BaseInlineForm(forms.ModelForm):
    """
    Abstract class to describe the basic inline (ie. in-the-wall) content creation form
    """
    is_inline = True
    error_css_class = 'error'
    required_css_class = 'required'

    def getName(self):
        """
        Return a friendly name for this form, usually used as the tab label
        """
        return self.Meta.model.__name__

    publisher_id = forms.IntegerField(required = True, widget = widgets.HiddenInput)

    class Meta:
        fields = ('text', 'permissions', 'language', )
        widgets = {
            'text':     widgets.Textarea(attrs = {'rows': 3, 'cols': 60}),
        }
        
class BaseRegularForm(forms.ModelForm):
    """
    A regular form is a form which is displayed on a full page
    """
    is_inline = False
    
    class Meta:
        fields = ('text', 'permissions', 'language', )
        widgets = {
            'text':     widgets.Textarea(attrs = {'rows': 3, 'cols': 60}),
        }

class ConfigurationForm(BaseRegularForm):
    """
    The main TN configuration form
    """
    
    class Meta:
        pass
