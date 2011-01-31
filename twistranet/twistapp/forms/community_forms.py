from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields

from twistranet.twistapp.forms.base_forms import BaseForm
from twistranet.twistapp.lib import permissions
from twistranet.twistapp.forms.widgets import ResourceWidget, PermissionsWidget
from  twistranet.twistapp.lib.log import log

class CommunityForm(BaseForm):
    """
    Community edition.
    """
    class Meta:
        from twistranet.twistapp.models import Community
        model = Community
        fields = ('title', 'description', 'picture', 'permissions', )

        widgets = {
            "picture":              ResourceWidget(),   
            "permissions":          PermissionsWidget(),
        }

class AdministrationForm(CommunityForm):
    """
    Global community edition form.
    This holds the global-community specific configuration options.
    """
    domain = forms.URLField(
        label = "Base URL of your site",
        required = True,
        )
    
    class Meta:
        from twistranet.twistapp.models import GlobalCommunity
        model = GlobalCommunity
        fields = (
            "site_name", 
            "baseline", 
            "permissions",
            "domain",
        )
        
