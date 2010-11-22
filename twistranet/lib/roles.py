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
    defined_values = []
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
        
    def allowed_by(self, permission_set):
        """
        Return True if current role is in the given _permissionmapping.QuerySet object
        """
        return permission_set.filter(role = self.value).exists()
        

# Global roles.
public = Role(1)
network = Role(3)
owner = Role(4)
system = Role(15)


# # Account roles
# account_network = Role(3, implied = (authenticated, ))          # Accessible only for ppl in my network
# 
# # Community roles
# community_member = Role(4, implied = (authenticated, ))         # === ntwk ?
# community_manager = Role(5, implied = (community_member, ))     # === owner(s) ?
# 
# # Account roles from a content point of view
# content_public = Role(6, implied = (authenticated, ))    # Special permission: same as publishers's account can_view permission
# content_network = Role(7, implied = (authenticated, ))
# content_community_member = Role(8, implied = (authenticated, ))             # Same as content_network but for community members
# content_community_manager = Role(9, implied = (content_community_member, )) # Content restricted to community managers
# content_author = Role(10, implied = (content_network, ))                    # Synonymous for roles.owner
# 
# # The great chiefs (for both account and content stuff)
# owner = content_author                                                      # For actions of the author or owner of an element
# administrator = Role(14, implied = (content_network, content_community_manager, community_manager, ))
# system = Role(15, implied = (administrator, content_author, ))



