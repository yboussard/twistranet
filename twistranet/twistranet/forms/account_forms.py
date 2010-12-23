from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields

from twistranet.twistranet.lib import permissions
from twistranet.twistranet.forms.widgets import ResourceWidget
from twistranet.twistranet.models import UserAccount
from twistranet.twistranet.forms.base_forms import BaseForm

class UserAccountForm(BaseForm):
    """
    User account edition.
    """    
    error_css_class = 'error'
    required_css_class = 'required'


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


