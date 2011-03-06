from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate

from twistranet.twistapp.lib import permissions
from twistranet.twistapp.forms.widgets import ResourceWidget
from twistranet.twistapp.models import UserAccount, Account
from twistranet.twistapp.forms.base_forms import BaseForm
from twistranet.tagging.fields import TagsFormField
from twistranet.tagging.models import Tag

class UserAccountForm(BaseForm):
    """
    User account edition.
    """    
    title = fields.CharField(
        label = _("Your name"),
        help_text = _("Enter your full name (eg. Firstname Lastname) as you want it to be displayed to other users."),
    )
    
    description = fields.CharField(
        label = _("About you"),
        help_text = _("Present yourself in a few lines. What are you working on? What do you like besides work?"),
        widget = widgets.Textarea(),
    )
    
    tags = TagsFormField(
        label = _("Keywords about you"),
        help_text = _("Enter what you do, what you like, ..."),
        required = False,
        queryset = Tag.objects.all(),
    )

    class Meta:
        model = UserAccount
        fields = ('title', 'description', 'tags', 'picture', )
        widgets = {
            "picture":          ResourceWidget(),
        }

class UserAccountCreationForm(forms.Form):
    """
    User Creation form.
    We add a few things to make this shiny.
    """
    first_name = forms.CharField(
        max_length = 40,
        label = _("First name"),
    )
    last_name = forms.CharField(
        max_length = 40,
        label = _("Last name"),
    )
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
    make_admin = forms.BooleanField(
        required = False,
        label = _("Invite as an administrator?")
    )
    invite_message = forms.CharField(
        required = False, 
        widget = widgets.Textarea(),
        label = _("Invitation message"),
        help_text = _("If given, this text will be added to the user when sending the invitation."),
    )
    
    class Meta:
        pass

class ChangePasswordForm(forms.Form):
    """
    Password reset form.
    """
    password = forms.CharField(
        label = _("Enter your current password"),
        widget=forms.PasswordInput,
    )
    new_password = forms.CharField(
        label = _("Enter your new password"),
        widget=forms.PasswordInput,
    )
    confirm = forms.CharField(
        label = _("Confirm your new password"),
        help_text = _("Enter the same password as above, for verification."),
        widget=forms.PasswordInput,
    )
    
    def clean_password(self,):
        # Double check username according to currently logged-in user
        username = Account.objects._getAuthenticatedAccount().user.username
        password = self.cleaned_data.get('password')
        if password:
            user_cache = authenticate(username=username, password=password)
            if user_cache is None:
                raise forms.ValidationError(_("Invalid password."))
            elif not user_cache.is_active:
                raise RuntimeError("Inactive account! Should never reach there.")
            else:
                return "(valid)"        # Avoid propagating the clean password...

    def clean_confirm(self,):
        password = self.cleaned_data.get("new_password", "")
        confirm = self.cleaned_data["confirm"]
        if password != confirm:
            raise forms.ValidationError(_("The two password fields didn't match."))
        return confirm
