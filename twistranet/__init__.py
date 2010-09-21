
# List of registered content types for this application
from twistranet.models import ContentRegistry, StatusUpdate
from twistranet.forms.contentforms import StatusUpdateForm

ContentRegistry.register(StatusUpdate, StatusUpdateForm)    

