from django import forms

from twistranet.forms import BaseContentForm
from helloworld.models import HelloWorld

class HelloWorldForm(BaseContentForm):
    """
    The famous "Hello, World!" example.
    """
    # subject = forms.CharField(max_length=100)
    # message = forms.CharField()
    # sender = forms.EmailField()
    # cc_myself = forms.BooleanField(required=False)
    class Meta(BaseContentForm.Meta):
        model = HelloWorld
        fields = ('scope',)
    
