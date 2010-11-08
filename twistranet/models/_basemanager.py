import inspect, pprint
from django.db import models
from django.contrib.auth.models import User

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
        """
        # We dig into the stack frame to find the request object.
        from account import Account, AnonymousAccount, UserAccount

        frame = inspect.currentframe()
        try:
            while frame:
                next_found = False
                local_viewed = False
                for mbr in inspect.getmembers(frame):
                    if mbr[0] == 'f_locals':
                        local_viewed = True
                        _locals = mbr[1]
    
                        # Check for a request.user User object
                        if _locals.has_key('request'):
                            u = getattr(_locals['request'], 'user', None)
                            if isinstance(u, User):
                                # We use this instead of the get_profile() method to avoid an infinite recursion here.
                                # We mimic the _profile_cache behavior of django/contrib/auth/models.py to avoid doing a lot of requests on the same object
                                if not hasattr(u, '_account_cache'):
                                    u._account_cache = UserAccount.objects.__booster__.get(user__id__exact = u.id)
                                    u._account_cache.user = u
                                return u._account_cache
                
                        # Check for an __acount__ variable holding a generic Account object
                        if _locals.has_key('__account__') and isinstance(_locals['__account__'], Account):
                            return _locals['__account__']
                    
                        # Locals inspected and next found => break here
                        if next_found:
                            break
        
                    if mbr[0] == 'f_back':
                        # Inspect caller
                        next_found = True
                        frame = mbr[1]
                        if local_viewed:
                            break
                            
            # Didn't find anything. We must be anonymous.
            return AnonymousAccount()

        finally:
            # Avoid circular refs
            frame = None
            stack = None
            del _locals


    # Backdoor for performance purposes. Use it at your own risk as it breaks security.
    @property
    def __booster__(self):
        return super(BaseManager, self).get_query_set()
