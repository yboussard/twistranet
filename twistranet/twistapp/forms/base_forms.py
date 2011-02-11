from django import forms
from django.db import models
from django.forms import widgets

from twistranet.twistapp.forms.widgets import PermissionsWidget
from twistranet.twistapp.forms.fields import PermissionsFormField
from twistranet.twistapp.lib.log import log

class BaseEmptyForm(forms.ModelForm):
    """
    A base, dummy, empty form used as a base for all other TN forms.
    """
    error_css_class = 'error'
    required_css_class = 'required'
    

class BaseForm(BaseEmptyForm):
    """
    A base TN form
    with the usual permission field
    and possible resource fields
    """
    def __init__(self, *args, **kw):
        """
        Overload widget rendering: we have to provide the model so that the PermissionsWidget
        will find which permissions to display.
        Note that we only do so on forms with a 'permissions' field.
        XXX TODO: Move part of this code in the model
        """
        super(BaseForm, self).__init__(*args, **kw)
        from twistranet.twistapp.models.community import Community
        from twistranet.twistapp.models.account import UserAccount
        # Check if has permissions field
        if self.fields.has_key('permissions'):
            publisher = self.initial.get("publisher", getattr(self.instance, "publisher", None))
            permissions = self.instance.permission_templates.permissions()
            if publisher:
                if issubclass(publisher.model_class, UserAccount):
                    permissions = [ p for p in permissions if not p.get("disabled_for_useraccount", False) ]
                if issubclass(publisher.model_class, Community):
                    permissions = [ p for p in permissions if not p.get("disabled_for_community", False) ]
            self.fields['permissions'].choices = [ (p["id"], p["name"], p["description"]) for p in permissions ]
            
        for field_name in ('picture', 'file', 'browsed_resource'):
            if self.fields.has_key(field_name):
                publisher = self.initial.get("publisher", getattr(self.instance, "publisher", None))
                if publisher :
                    # XXX FIXME > when editing account publisher is often 
                    # 'all twistranet', and of course only admin has the rights
                    if getattr(publisher, 'slug')==u'all_twistranet' :
                        publisher = self.instance.account
                    self.fields[field_name].widget.publisher = publisher

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
    A regular form is a form which is displayed on a full page
    """
    is_inline = False
    allow_creation = True
    allow_edition = True
        
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
