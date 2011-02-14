from django import forms
from django.db import models
from django.forms import widgets

from twistranet.twistapp.models import Resource
from fields import ResourceFormField
from base_forms import BaseForm

class ResourceForm(forms.ModelForm):
    """
    Abstract class to describe the basic resource creation form
    """
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        model = Resource

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
    
    def __init__(self, *args, **kw):
        """
        Taken from base_form.
        XXX TODO: Make this upload to the community instead of the current account if we're on a community.
        """
        super(ResourceBrowserForm, self).__init__(*args, **kw)
        from twistranet.twistapp.models.community import Community
        from twistranet.twistapp.models.account import Account, UserAccount
        from twistranet.twistapp.forms.fields import PermissionsFormField
        from twistranet.twistapp.forms.fields import ResourceFormField

        # Special fields tweaks
        for field_name, field in self.fields.items():
            # File browser field tweaks: give publisher to the field so that we can upload it safely.
            if isinstance(field, ResourceFormField):
                deepest_publisher = None
                if self.initial.get("publisher", None):
                    deepest_publisher = self.initial['publisher']
                else:
                    # No instance, we must be creating something.
                    # XXX TODO: Fix the case of an image set when creating a Community,
                    # because it will be put on the account instead of the community.
                    # We use 100% default values.
                    deepest_publisher = None
                    
                # Go up the "deepest_publisher" object to find the correct account
                publisher = None
                if deepest_publisher: 
                    while deepest_publisher and not isinstance(deepest_publisher, Account):
                        deepest_publisher = deepest_publisher.publisher
                    
                    # Publisher is now either an Account or None.
                    # But we double check if we've got the rights on it.
                    if deepest_publisher and deepest_publisher.can_edit:
                        publisher = deepest_publisher

                # Set field parameters
                field.widget.publisher = publisher
                field.widget.publisher_id = publisher and publisher.id

