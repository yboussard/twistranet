"""
TwistraNet Custom Permission model.

We can't use Django's default permission model as ours is role-based and object-dependant.
Django is user-(or group-)based and not object-dependant as of today.

Difference between a role and a group? A role might be different for the same user on different objects.
"""
# Global roles.
public = 1
network = 2
manager = 4
owner = 8
system = 16

# Special 'intelligent' roles.
# NEVER compare to this, they're just used to be resolved at save-time.

# If publisher is a community => Network. Else, Owner.
def owner_or_network_role(object):
    from twistranet.twistapp.models import Community
    if isinstance(object.publisher.model_class, Community):
        return network
    return owner
