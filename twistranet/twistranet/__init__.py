# Import models first
from twistranet.twistranet.models import *

# List of registered content and account types for this application
# from twistranet.twistranet.forms.content_forms import StatusUpdateForm, DocumentForm

# Do the mandatory database checkup and initial buiding
from twistranet.twistranet.lib import dbsetup
# dbsetup.bootstrap()                      # XXX: TODO: Only call it explicitly if you need to.
dbsetup.check_consistancy()
