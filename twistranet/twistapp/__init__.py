from twistranet import __author__, VERSION
__version__ = '.'.join(map(str, VERSION))

# Import / Load config & logger
from twistranet.twistapp.lib.log import log

# Then import models
from twistranet.twistapp.models import *

# Import forms because they're not automatically imported
from twistranet.twistapp.forms import community_forms, resource_forms

# Do the mandatory database checkup and initial buiding
from twistranet.core import bootstrap
bootstrap.check_consistancy()

# monkey patches
from twistranet.core import patches

log.debug("Twistranet loaded successfuly!")