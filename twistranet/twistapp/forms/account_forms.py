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
    User account creation.
    """    
    class Meta:
        model = UserAccount
        fields = ('user', 'title', 'description', 'picture', 'permissions', )

        widgets = {
            "picture":          ResourceWidget(),
        }


