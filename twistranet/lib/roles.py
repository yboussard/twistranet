"""
TwistraNet Custom Permission model.

We can't use Django's default permission model as ours is role-based and object-dependant.
Django is user-(or group-)based and not object-dependant as of today.

Difference between a role and a group? A role might be different for the same user on different objects.
"""
class Role:
    """
    A role is a bit set on an integer.
    That means there can't be (as of today) more than 31 roles in a twistranet app...
    """
    def __init__(self, value, implied = None):
        """
        value is an integer between 1 and 62.
        implied_roles is a list of roles the current role implies as defined in the at_least() method.
        """
        if value in self.__class__.defined_values:
            raise ValueError("Role %d already exists." % value)
        self.__class__.defined_values.append(value)
        self.value = value
        self.implied_values = (value,)
        if implied:
            for role in implied:
                self.implied_values = self.implied_values + role.implied_values
        
    def implied(self):
        """
        Return implied roles bitmask
        """
        return self.implied_values
        
    def __trunc__(self):
        """
        Convert self to integer
        """
        return self.value
        
Role.defined_values = []

# Global roles
anonymous = Role(1)
authenticated = Role(2, implied = (anonymous, ))

# Account roles
account_network = Role(3, implied = (authenticated, ))          # Accessible only for ppl in my network

# Community roles
community_member = Role(4, implied = (authenticated, ))
community_manager = Role(5, implied = (community_member, ))

# Account roles from a content point of view
content_public = Role(6, implied = (authenticated, ))    # Special permission: same as author's account can_view permission
content_network = Role(7, implied = (authenticated, ))
content_community_member = Role(8, implied = (authenticated, ))   # Same as content_network but for community members
content_community_manager = Role(9, implied = (content_community_member, )) # Content restricted to community managers
content_author = Role(10, implied = (content_network, ))

# The great chiefs
administrator = Role(14, implied = (content_network, content_community_manager, community_manager, ))
system = Role(15, implied = (administrator, content_author, ))



