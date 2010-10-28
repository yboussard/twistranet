
# List of registered content types for this application
from twistranet.lib import ContentRegistry
from helloworld.models import HelloWorld
from helloworld.forms import HelloWorldForm

ContentRegistry.register(HelloWorld, HelloWorldForm)    

