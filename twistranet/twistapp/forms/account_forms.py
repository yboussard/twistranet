from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields
from django.utils.translation import ugettext as _

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

class UserAccountCreationForm(forms.Form):
    """
    User Creation form.
    We add a few things to make this shiny.
    """
    first_name = forms.CharField(max_length = 40)
    last_name = forms.CharField(max_length = 40)
    username = forms.CharField(
        label = _("Login name"),
        max_length = 30
    )
    email = forms.EmailField(max_length = 40)
    password = forms.CharField(
        widget = widgets.PasswordInput(),
        label = _("Choose your password"),
    )
    password_confirm = forms.CharField(
        widget = widgets.PasswordInput(),
        label = _("Confirm your password"),
    )
    class Meta:
        pass

class UserInviteForm(forms.Form):
    """
    User account creation.
    """
    email = forms.EmailField()
    invite_message = forms.CharField(required = False, widget = widgets.Textarea())
    
    class Meta:
        pass

