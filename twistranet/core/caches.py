"""
Various caching help functions and classes.
"""
from django.core.cache import cache

DEFAULT_CACHE_DELAY = 60 * 60           # Default cache delay is 1hour. It's quite long.
USERACCOUNT_CACHE_DELAY = 60 * 3        # 3 minutes here. This is used to know if a user is online or not.

class _AbstractCache(object):
    """
    Abstract cache management class.
    A cache class manages data about a whole population.
    It is instanciated with a specific instance of this cache object.
    """
    delay = DEFAULT_CACHE_DELAY
    
    def __init__(self, key_prefix):
        """
        We store the key prefix for easy values retrieval
        """
        # Save key profile AND save an empty cache value to use as an optional global timeout
        self.key_prefix = key_prefix
        
    def _get(self, attr, default = None):
        """
        Return attr from the cache or default value
        """
        return cache.get("%s#%s" % (self.key_prefix, attr), default)
        
    def _set(self, attr, value):
        cache.set("%s#%s" % (self.key_prefix, attr), value, self.delay)

class UserAccountCache(_AbstractCache):
    
    delay = USERACCOUNT_CACHE_DELAY
    
    def __init__(self, useraccount_or_id):
        """
        Instanciate a cache from given user (or userid)
        """
        # Instanciate cache
        from twistranet.twistapp import Twistable
        if isinstance(useraccount_or_id, Twistable):
            useraccount_or_id = useraccount_or_id.id
        super(UserAccountCache, self).__init__("UA%d" % useraccount_or_id)

    # Online information
    def get_online(self):       return self._get("online", False)
    def set_online(self, v):    return self._set("online", v)
    online = property(get_online, set_online)
        


