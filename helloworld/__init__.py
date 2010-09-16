
# List of registered content types for this application
from TwistraNet.content.models import ContentRegistry
from TwistraNet.helloworld.models import HelloWorld
from TwistraNet.helloworld.forms import HelloWorldForm

ContentRegistry.register(HelloWorld, HelloWorldForm)    

