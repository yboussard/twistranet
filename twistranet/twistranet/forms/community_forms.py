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
    error_css_class = 'error'
    required_css_class = 'required'
    
    class Meta:
        from twistranet.twistranet.models import Community
        model = Community
        fields = ('title', 'description', 'picture', 'permissions', )

        widgets = {
            "picture":          ResourceWidget(),
        }

