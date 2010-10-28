
# List of registered content types for this application
from twistranet.lib import form_registry
from helloworld.models import HelloWorld
from helloworld.forms import HelloWorldForm

form_registry.register(HelloWorldForm)    

