from django import forms
from django.db import models
from django.forms import widgets

class BaseContentForm(forms.ModelForm):
    """
    Abstract class to describe the basic content form
    """    
    error_css_class = 'error'
    required_css_class = 'required'

    def getName(self):
        """
        Return a friendly name for this form, usually used as the tab label
        """
        return self.Meta.model.__name__

    publisher_id = forms.IntegerField(required = True, widget = widgets.HiddenInput)

    class Meta:
        fields = ('text', 'permissions', 'language', )
        widgets = {
            'text':     widgets.Textarea(attrs = {'rows': 3, 'cols': 60}),
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
        from twistranet.models import StatusUpdate
        model = StatusUpdate
        fields = BaseContentForm.Meta.fields
        widgets = BaseContentForm.Meta.widgets
