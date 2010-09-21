from django import forms
from django.db import models
from django.forms.widgets import HiddenInput

class BaseContentForm(forms.ModelForm):
    """
    Abstract class to describe the basic content form
    """    
    def getName(self):
        """
        Return a friendly name for this form, usually used as the tab label
        """
        return self.Meta.model.__name__

    class Meta:
        fields = ('content_type', 'public', )
        widgets = {
            "content_type": HiddenInput,
            }

class StatusUpdateForm(BaseContentForm):
    """
    The famous status update.
    """
    # subject = forms.CharField(max_length=100)
    # message = forms.CharField()
    # sender = forms.EmailField()
    # cc_myself = forms.BooleanField(required=False)
    
    class Meta(BaseContentForm.Meta):
        from twistranet.models.contentmodels import StatusUpdate
        model = StatusUpdate
        fields = BaseContentForm.Meta.fields + ('text', )
