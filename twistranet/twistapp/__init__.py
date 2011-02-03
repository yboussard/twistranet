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

# Ok, I know this is ugly, but we have to hotfix django's authenticate() method.
# We do so to allow auth backends to access profiles.
# In fact, we only 'twistauthenticate' SystemAccount during this step.
from django.contrib import auth
def authenticate(**credentials):
    """
    If the given credentials are valid, return a User object.
    """
    from twistranet.twistapp.models import account
    __account__ = account.SystemAccount.get()           # This is what we just add.
    for backend in auth.get_backends():
        try:
            user = backend.authenticate(**credentials)
        except TypeError:
            # This backend doesn't accept these credentials as arguments. Try the next one.
            continue
        if user is None:
            continue
        # Annotate the user object with the path of the backend.
        user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
        return user

auth.authenticate = authenticate
log.info("Hotfixed django.contrib.auth.authenticate to allow all profiles access during authentication")

log.debug("Twistranet loaded successfuly!")