
# List of registered content and account types for this application
from twistranet.models import ContentRegistry, StatusUpdate
from twistranet.forms.contentforms import StatusUpdateForm
ContentRegistry.register(StatusUpdate, StatusUpdateForm)    

# Do the mandatory database checkup and initial buiding
from twistranet.models import dbsetup
dbsetup.bootstrap()
dbsetup.check_consistancy()

