from django import forms
from django.db import models
from django.forms import widgets
from django.forms import fields

from twistranet.twistranet.lib import permissions
from twistranet.twistranet.forms.widgets import ResourceWidget
from twistranet.twistranet.models import UserAccount

class UserAccountForm(forms.ModelForm):
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



