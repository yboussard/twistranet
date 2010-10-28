
# List of registered content and account types for this application
from twistranet.models import StatusUpdate, Notification
from twistranet.forms.contentforms import StatusUpdateForm
from twistranet.lib import ContentRegistry
ContentRegistry.register(StatusUpdate, StatusUpdateForm)
ContentRegistry.register(Notification, None, False)

# Do the mandatory database checkup and initial buiding
from twistranet.lib import dbsetup
dbsetup.bootstrap()                      # XXX: TODO: Only call it explicitly if you need to.
dbsetup.check_consistancy()

