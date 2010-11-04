from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields

from twistranet.lib import permissions

class CommunityForm(forms.ModelForm):
    """
    Community edition
    """    
    error_css_class = 'error'
    required_css_class = 'required'
    permissions = fields.ChoiceField(choices = permissions.community_templates.get_choices())

    class Meta:
        from twistranet.models import Community
        model = Community
        fields = ('name', 'screen_name', 'description', '_picture', 'permissions', )

        # fields = ('text', 'permissions', 'language', )
        widgets = {
            'permissions':     widgets.Select(),
        }

