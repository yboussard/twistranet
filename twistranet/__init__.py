
# List of registered content and account types for this application
from twistranet.models import ContentRegistry, StatusUpdate, Notification
from twistranet.forms.contentforms import StatusUpdateForm
ContentRegistry.register(StatusUpdate, StatusUpdateForm)
ContentRegistry.register(Notification, None, False)

# Do the mandatory database checkup and initial buiding
from twistranet.models import dbsetup
dbsetup.bootstrap()                      # XXX: TODO: Only call it explicitly if you need to.
dbsetup.check_consistancy()

