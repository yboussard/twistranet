from django import forms
from django.db import models
from django.forms import widgets
from twistranet.twistranet.forms.widgets import PermissionsWidget


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kw):
        """
        Overload widget rendering: we have to provide the model so that the PermissionsWidget
        will find which permissions to display.
        """
        from twistranet.twistranet.models.community import Community
        from twistranet.twistranet.models.account import UserAccount
        super(BaseForm, self).__init__(*args, **kw)
        publisher = self.initial.get("publisher", None)
        permissions = self.instance.permission_templates.permissions()
        if isinstance(publisher, UserAccount):
            permissions = [ p for p in permissions if not p.get("disabled_for_useraccount", False) ]
        if isinstance(publisher, Community):
            permissions = [ p for p in permissions if not p.get("disabled_for_community", False) ]
        self.fields['permissions'].choices = [ (p["id"], p["name"]) for p in permissions ]

    # permissions = forms.ChoiceField(choices = (), widget = PermissionsWidget)

class BaseInlineForm(BaseForm):
    """
    Abstract class to describe the basic inline (ie. in-the-wall) content creation form
    """
    is_inline = True
    error_css_class = 'error'
    required_css_class = 'required'

    publisher_id = forms.IntegerField(required = True, widget = widgets.HiddenInput)

    def getName(self):
        """
        Return a friendly name for this form, usually used as the tab label
        """
        return self.Meta.model.__name__

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
