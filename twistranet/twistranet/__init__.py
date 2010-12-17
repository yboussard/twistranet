# Import / Load config
from twistranet.twistranet.conf import defaults

# Then import models
from twistranet.twistranet.models import *

# Import forms because they're not automatically imported
from twistranet.twistranet.forms import community_forms, resource_forms

# Do the mandatory database checkup and initial buiding
from twistranet.twistranet.lib import dbsetup
# dbsetup.bootstrap()                      # XXX: TODO: Only call it explicitly if you need to.
dbsetup.check_consistancy()
