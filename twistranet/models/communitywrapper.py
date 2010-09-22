from django.db.models import Q

from community import Community

class CommunityWrapper:
    """
    This class is used as a pivot between an account and its related content.
    It's meant to be instanciated by the Account class and provide helper methods
    to access community information relevant to the current account.

    This replaces the Manager classes for our security model.
    
    It's the base of the security model!!
    """
    def __init__(self, account):
        self._account = account

    @property
    def authorized(self):
        """
        Return a queryset of populated objects
        """
        # If system account, return all available communities
        if self._account.account_type == "SystemAccount":
            self._account.systemaccount
            return Community._objects.get_query_set()
        
        return Community._objects.filter(
            (
                # Public communities
                Q(scope = "anonymous")
            ) | (
                # Auth-only communities
                Q(scope = "authenticated")
            ) | (
                # Communities I'm a member of
                Q(members = self._account)
            )
        ).distinct()

    @property
    def my(self):
        """
        Return communities I'm a member of.
        """
        return Community._objects.filter(members = self._account)

    def join(self, community):
        """
        Join a community (securely)
        """
        return community.join(self._account)
        
    def leave(self, community):
        """
        Leave a community (securely)
        """
        return community.leave(self._account)

    @property
    def global_(self):
        """
        Return the global community. May raise if no access right.
        """
        return self.authorized.get(community_type = "GlobalCommunity")
        
    @property
    def admin(self):
        """
        Return the admin community / communities
        """
        return self.authorized.filter(community_type = "AdminCommunity")

    def __getattr__(self, name):
        return getattr(self.authorized, name)


