from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields

from twistranet.twistapp.lib import permissions
from twistranet.twistapp.forms.widgets import ResourceWidget
from twistranet.twistapp.models import UserAccount
from twistranet.twistapp.forms.base_forms import BaseForm

class UserAccountForm(BaseForm):
    """
    User account edition.
    """    
    class Meta:
        model = UserAccount
        fields = ('title', 'description', 'picture', )

        widgets = {
            "picture":          ResourceWidget(),
        }

class UserAccountCreationForm(UserAccountForm):
    """
    User Creation form.
    We add a few things to make this shiny.
    """
    # slug = forms.CharField()
    email = forms.EmailField()
    class Meta:
        model = UserAccount
        fields = ('slug', 'title', 'description', 'email', )
        widgets = {
        }

class UserInviteForm(forms.Form):
    """
    User account creation.
    """
    email = forms.EmailField()
    invite_message = forms.CharField(required = False, widget = widgets.Textarea())
    
    class Meta:
        pass

