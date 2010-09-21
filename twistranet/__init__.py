
# List of registered content types for this application
from twistranet.models.contentmodels import ContentRegistry
from twistranet.models.contentmodels import StatusUpdate
from twistranet.forms.contentforms import StatusUpdateForm

ContentRegistry.register(StatusUpdate, StatusUpdateForm)    

