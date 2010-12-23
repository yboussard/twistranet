"""
Notifier handlers.
Some send emails, some insert 'notification' objects in TN, etc.

We use classes instead of functions to allow inheritance between handlers.

Don't forget to connect to your signals with 'weak = False' !!
"""
import logging
from twistranet.log import log


class NotifierHandler(object):
    def __call__(self, sender, **kwargs):
        """
        This is where our handlers get called.
        Always call your parent first to populate your class instance
        and check various stuff on it.s
        """


class LogHandler(NotifierHandler):
    '''
    Just prints a log message for what it's been called for.
    '''
    def __init__(self, level = logging.DEBUG):
        self.level = level

    def __call__(self, sender, **kwargs):
        log.log(self.level, "%s %s" % (sender, kwargs))


class NotificationHandler(NotifierHandler):
    """
    This adds a Notification object just right into your twistranet site.
    It is somewhat internationalized.

    You can customize the displayed description upon class creation: the message
    will be _'ed with %(xxx)s values filled from a dictionary.
    """
    def __init__(self, owner_arg, publisher_arg, message, permissions = "public"):
        """
        Store the message for future use.
        owner_arg and publisher_arg will be used to create the underlying content.
        owner_arg defaults to SystemAccount
        publisher_arg defaults to owner arg's publisher.
        """
        self.owner_arg = owner_arg
        self.publisher_arg = publisher_arg
        self.message = message
        self.permissions = permissions

    def __call__(self, sender, **kwargs):
        """
        We add the Notification object on behalf of SystemAccount.
        """
        from twistranet.twistranet.models import Twistable
        from twistranet.twistranet.models import SystemAccount
        from twistranet.notifier.models import Notification

        # Prepare the message dict.
        # We use title_or_description on each Twistable argument to display it.
        message_dict = {}
        for param, value in kwargs.items():
            if isinstance(value, Twistable):
                message_dict[param] = value.html_link

        # We force __account__ to fake user login.
        system = SystemAccount.get()
        __account__ = system
        owner = kwargs.get(self.owner_arg, system)
        publisher = kwargs.get(self.publisher_arg, owner.publisher)
        n = Notification(
            publisher = publisher,
            owner = owner,
            title = "",
            description = self.message % message_dict,
            permissions = self.permissions,
        )
        n.save()



