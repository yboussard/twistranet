# Import models first
from twistranet.core.models import *

# List of registered content and account types for this application
# from twistranet.core.forms.content_forms import StatusUpdateForm, DocumentForm

# Do the mandatory database checkup and initial buiding
from twistranet.core.lib import dbsetup
# dbsetup.bootstrap()                      # XXX: TODO: Only call it explicitly if you need to.
dbsetup.check_consistancy()
