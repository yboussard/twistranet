from django import forms
from django.db import models
from django.forms import widgets

from django.utils.translation import ugettext as _

from twistranet.tagging.fields import TagsFormField
from twistranet.tagging.models import Tag

from twistranet.twistapp.forms.widgets import PermissionsWidget
from twistranet.twistapp.forms.fields import PermissionsFormField
from twistranet.twistapp.lib.log import log

class BaseEmptyForm(forms.ModelForm):
    """
    A base, dummy, empty form used as a base for all other TN forms.
    We do some widget tweaking here.
    """
    error_css_class = 'error'
    required_css_class = 'required'
    
    def __init__(self, *args, **kw):
        """
        Overload widget rendering: we have to provide the model so that the PermissionsWidget
        will find which permissions to display.
        Note that we only do so on forms with a 'permissions' field.
        XXX TODO: Move part of this code in the model
        """
        super(BaseEmptyForm, self).__init__(*args, **kw)
        from twistranet.twistapp.models.community import Community
        from twistranet.twistapp.models.account import Account, UserAccount
        from twistranet.twistapp.forms.fields import PermissionsFormField
        from twistranet.twistapp.forms.fields import ResourceFormField

        # Special fields tweaks
        for field_name, field in self.fields.items():
            # Permission field tweak: just display the right options for the right object
            if isinstance(field, PermissionsFormField):
                publisher = self.initial.get("publisher", getattr(self.instance, "publisher", None))
                permissions = self.instance.permission_templates.permissions()
                if publisher:
                    if issubclass(publisher.model_class, UserAccount):
                        permissions = [ p for p in permissions if not p.get("disabled_for_useraccount", False) ]
                    if issubclass(publisher.model_class, Community):
                        permissions = [ p for p in permissions if not p.get("disabled_for_community", False) ]
                field.choices = [ (p["id"], p["name"], p["description"]) for p in permissions ]
            
            # File browser field tweaks: give publisher to the field so that we can upload it safely.
            if isinstance(field, ResourceFormField):
                deepest_publisher = None
                if self.initial.get("publisher", None):
                    deepest_publisher = self.initial['publisher']
                elif self.instance:
                    deepest_publisher = self.instance
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


class BaseForm(BaseEmptyForm):
    """
    A base TN form
    with the usual permission field
    and possible resource fields
    """
    _publisher_cache = None
    
    permissions = PermissionsFormField(choices = (), widget = PermissionsWidget())
    publisher_id = forms.IntegerField(required = False, widget = widgets.HiddenInput)

    def getName(self):
        """
        Return a friendly name for this form, usually used as the tab label
        """
        return self.Meta.model.__name__

class BaseInlineForm(BaseForm):
    """
    Abstract class to describe the basic inline (ie. in-the-wall) content creation form
    """
    is_inline = True
    error_css_class = 'error'
    required_css_class = 'required'

    class Meta:
        fields = ('permissions', )
        
class BaseRegularForm(BaseForm):
    """
    A regular form is a form which is displayed on a full page.
    """
    is_inline = False
    allow_creation = True
    allow_edition = True

    tags = TagsFormField(
        label = "Keywords",
        help_text = "Enter relevant keywords about your content.",
        required = False,
        queryset = Tag.objects.all(),
    )
        
    class Meta:
        fields = ('text', 'permissions', )
        widgets = {
            'text':     widgets.Textarea(attrs = {'rows': 3, 'cols': 60}),
        }

class ConfigurationForm(BaseRegularForm):
    """
    The main TN configuration form
    """
    class Meta:
        pass
