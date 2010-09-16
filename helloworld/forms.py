from django import forms

from TwistraNet.content.forms import ContentForm
from TwistraNet.helloworld.models import HelloWorld

class HelloWorldForm(ContentForm):
    """
    The famous "Hello, World!" example.
    """
    # subject = forms.CharField(max_length=100)
    # message = forms.CharField()
    # sender = forms.EmailField()
    # cc_myself = forms.BooleanField(required=False)
    class Meta(ContentForm.Meta):
        model = HelloWorld
        fields = ContentForm.Meta.fields
    
