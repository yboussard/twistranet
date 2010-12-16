from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields

from twistranet.twistranet.lib import permissions
from twistranet.twistranet.forms.widgets import ResourceWidget

class CommunityForm(forms.ModelForm):
    """
    Community edition.
    """    
    error_css_class = 'error'
    required_css_class = 'required'
    
    permissions = fields.ChoiceField(choices = permissions.community_templates.get_choices())

    class Meta:
        from twistranet.twistranet.models import Community
        model = Community
        fields = ('title', 'description', 'picture', 'permissions', )

        # fields = ('text', 'permissions', 'language', )
        widgets = {
            'permissions':      widgets.Select(),
            "picture":          ResourceWidget(),
        }



