"""
This is where default TN signals are registered
"""
import django.dispatch


# This signal is sent whenever a Twistable object is created/modified.
# It's sent last, to ensure all mandatory DB work is done before.
twistable_post_save = django.dispatch.Signal(
    providing_args = ["instance", "created", ],
)

# General notification signals.
# In most of those signals, the "publisher" argument is who this signal
# is normally targetting.

# This is triggered when a user is invited to TN
invite_user = django.dispatch.Signal(
    providing_args = ["target", "message", ]
)

# Here's how we send the reset password link
reset_password = django.dispatch.Signal(
    providing_args = ["target", "reset_password_absolute_url", ]
)

# This signal is sent when a user adds another one to its network
# Sender is the Account Model.
#   client is the Account who explicitly wants to add the other one
#   target is the Account targeted by this request
accept_in_network = django.dispatch.Signal(
    providing_args = ["client", "target", ],
)

# This is the same, but if the reciprocical acceptation is not settled (yet).
request_add_to_network = django.dispatch.Signal(
    providing_args = ["client", "target", ],
)

# This one is sent when a user in invited into a community.
invite_community = django.dispatch.Signal(
    providing_args = ["target", "community", ]
)

# This one is sent when a user actually (and explicitly) joins a community.
join_community = django.dispatch.Signal(
    providing_args = ["client", "community", ]
)

# This is when a user ASKS to join a community but is not immediately accepted.
request_join_community = django.dispatch.Signal(
    providing_args = ["client", "community", ]
)


