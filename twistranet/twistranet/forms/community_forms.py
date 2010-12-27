from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields

from twistranet.twistranet.forms.base_forms import BaseForm
from twistranet.twistranet.lib import permissions
from twistranet.twistranet.forms.widgets import ResourceWidget, PermissionsWidget
from twistranet.log import log

class CommunityForm(BaseForm):
    """
    Community edition.
    """
    class Meta:
        from twistranet.twistranet.models import Community
        model = Community
        fields = ('title', 'description', 'picture', 'permissions', )

        widgets = {
            "picture":          ResourceWidget(),   
            "permissions":          PermissionsWidget(),
        }

class GlobalCommunityForm(CommunityForm):
    """
    Global community edition.
    This is the same as communityform but with additional configuration
    """
    class Meta:
        from twistranet.twistranet.models import GlobalCommunity
        model = GlobalCommunity
        fields = ('title', 'description', 'picture', 'permissions', "site_name", "baseline", )
        
