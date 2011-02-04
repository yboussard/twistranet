# Ok, I know this is ugly, but we have to hotfix django's authenticate() method.
# We do so to allow auth backends to access profiles.
# In fact, we only 'twistauthenticate' SystemAccount during this step.
from django.contrib import auth
from twistranet.twistapp.models import account
from twistranet.twistapp.lib.log import *

def authenticate(**credentials):
    """
    If the given credentials are valid, return a User object.
    """
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
