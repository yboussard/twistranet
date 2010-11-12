from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields

from twistranet.lib import permissions

class CommunityForm(forms.ModelForm):
    """
    Create a form instance from POST data.
    >>> request = self.request
    >>> f = CommunityForm(request.POST)
    Save a new Community object from the form's data.
    >>> new_community = f.save()
    Create a form to edit an existing Community.
    >>> c = Community.objects.get(pk=1)
    >>> f = CommunityForm(instance=c)
    >>> f.save()
    Create a form to edit an existing Community, but use
    POST data to populate the form.
    >>> c = Community.objects.get(pk=1)
    >>> f = CommunityForm(request.POST, instance=c)
    >>> f.save()
    """    
    error_css_class = 'error'
    required_css_class = 'required'
    permissions = fields.ChoiceField(choices = permissions.community_templates.get_choices())

    class Meta:
        from twistranet.models import Community
        model = Community
        fields = ('title', 'description', 'picture', 'permissions', )

        widgets = {
            'permissions':     widgets.Select(),
        }



