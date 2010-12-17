"""
This is the main notifier service.
"""
from django.utils.translation import ugettext as _

from twistranet.twistranet.signals import *
import handlers

#twistable_post_save.connect(handlers.LogHandler(), weak = False)

join_community.connect(
    handlers.NotificationHandler(
        owner_arg = "client",
        publisher_arg = "community",
        message = _("""%(client)s joined %(community)s."""),
    ),
    weak = False,
)

accept_in_network.connect(
    handlers.NotificationHandler(
        owner_arg = "client",
        publisher_arg = "target",
        message = _("""%(client)s is now connected to %(target)s."""),
    ),
    weak = False,
)

