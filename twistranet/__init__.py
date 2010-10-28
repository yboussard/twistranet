
# List of registered content and account types for this application
from twistranet.forms.content_forms import StatusUpdateForm
from twistranet.lib import form_registry

form_registry.register(StatusUpdateForm)
# form_registry.register(DocumentForm)

# Do the mandatory database checkup and initial buiding
from twistranet.lib import dbsetup
dbsetup.bootstrap()                      # XXX: TODO: Only call it explicitly if you need to.
dbsetup.check_consistancy()

