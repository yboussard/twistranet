import inspect
from django.db import models
from django.contrib.auth.models import User

from scope import *

class BaseManager(models.Manager):
    """
    It's the base of the security model!!
    
    The base manager assumes that:
    - it's called from a view having an authenticated user
    - its target model has a manager called _objects which return the unprotected objects.
    - the target model has a 'scope' property which is used to define the model's object visibility.
        Must be one of ACCOUNTSCOPE_ANONYMOUS, ACCOUNTSCOPE_AUTHENTICATED or ACCOUNTSCOPE_MEMBERS for account
        or must be CONTENTSCOPE_PUBLIC, CONTENTSCOPE_NETWORK or CONTENTSCOPE_PRIVATE for content
    """

    def _getAuthenticatedAccount(self):
        """
        Dig the stack to find the authenticated account object.
        Return either a (possibly generic) account object or None.
        
        Views with a "request" parameter magically works with that.
        If you want to use a system account, declare a '__account__' variable in your caller function.
        XXX TODO: Check against circular references!
        """
        # We dig into the stack frame to find the request object.
        from account import Account
        _locals = {}
        try:
            for stack in inspect.stack():
                _locals = [ mbr[1] for mbr in inspect.getmembers(stack[0]) if mbr[0] == 'f_locals' ][0]

                # Check for a request.user User object
                if _locals.has_key('request') and hasattr(_locals['request'], 'user') and isinstance(_locals['request'].user, User):
                    return _locals['request'].user.get_profile()
                    
                # Check for an __acount__ variable holding a generic Account object
                if _locals.has_key('__account__') and isinstance(_locals['__account__'], Account):
                    return _locals['__account__']
                
                # Clean memory to avoid circular refs before continuing
                del stack
        finally:
            # Avoid circular refs
            stack = None
            del _locals
        

        