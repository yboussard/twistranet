from django import forms

from twistranet.forms import base_forms
from helloworld.models import HelloWorld
from twistranet.lib import form_registry

class HelloWorldForm(base_forms.BaseInlineForm):
    """
    The famous "Hello, World!" example.
    """
    # subject = forms.CharField(max_length=100)
    # message = forms.CharField()
    # sender = forms.EmailField()
    # cc_myself = forms.BooleanField(required=False)
    class Meta(base_forms.BaseInlineForm.Meta):
        model = HelloWorld
        # Usually, one should do fields = BaseContentForm.Meta.fields + ('myfield', ...)
        fields = ('permissions',)
    
form_registry.register(HelloWorldForm)    

