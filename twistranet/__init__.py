
# List of registered content types for this application
from TwistraNet.content.models import ContentRegistry
from TwistraNet.content.models import StatusUpdate
from TwistraNet.content.forms import StatusUpdateForm

ContentRegistry.register(StatusUpdate, StatusUpdateForm)    

