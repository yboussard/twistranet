from django import forms
from django.db import models
from django.forms import widgets

from django_twistranet.models import Resource
from fields import ResourceFormField
from base_forms import BaseForm

class ResourceForm(forms.ModelForm):
    """
    Abstract class to describe the basic resource creation form
    """
    error_css_class = 'error'
    required_css_class = 'required'

    # publisher_id = forms.IntegerField(required = True, widget = widgets.HiddenInput)

    class Meta:
        model = Resource
        # fields = ('text', 'permissions', 'language', )
        # widgets = {
        #     'text':     widgets.Textarea(attrs = {'rows': 3, 'cols': 60}),
        # }

class MediaForm(forms.Form):
    """
    This is a handy form to manage media resources.
    A media can be either a link or a file.
    This form abstracts completely the notion of media so you can produce content without a worry
    about where your attached media lies.
    """
    title = forms.CharField(max_length=50)
    file  = forms.FileField()
    url = forms.URLField()

class ResourceBrowserForm(forms.Form):
    """just a basic form to browse and upload resources
       used by wysiwyg editors
    """                                      
    
    browsed_resource = ResourceFormField(label='', allow_select=True, allow_upload=True, display_renderer=False)