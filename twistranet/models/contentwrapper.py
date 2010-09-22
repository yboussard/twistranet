from django.db.models import Q

from content import Content

class ContentWrapper:
    """
    This class is used as a pivot between an account and its related content.
    It's meant to be instanciated by the Account class and provide helper methods
    to access content information relevant to the current account.
    
    We also may have subclassed content's queryset but it seemed more efficient
    (ie. faster execution) to do explicit queries for each method.
    The drawback is that they're not chainable.  
    """
    def __init__(self, account):
        self._account = account

    @property
    def authorized(self):
        my_network = self._account.getMyNetwork()
        return Content._unsecured.filter(
            (
                # Public stuff by the people I follow
                Q(public = True)
            ) | (
                # Public AND private stuff from the people in my network
                Q(diffuser__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = self._account)
            )
        )

    @property
    def my(self):
        return self.authorized.filter(author = self._account)

    @property
    def followed(self):
        """
        Return content explicitly followed by the account
        """
        my_followed = self._account.getMyFollowed()
        my_network = self._account.getMyNetwork()
        return Content._unsecured.filter(
            (
                # Public stuff by the people I follow
                Q(diffuser__in = my_followed) & Q(public = True)
            ) | (
                # Public AND private stuff from the people in my network
                Q(diffuser__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = self._account)
            )
        )        

    def __getattr__(self, name):
        return getattr(self.authorized, name)
