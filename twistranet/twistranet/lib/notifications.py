"""
TwistraNet internal notifications system.
We use this to log short status message about what people do in TN.
"""

class Notifier(object):
    """
    Helper stateless class to manage notifications for various actions.
    Use the 'notifier' singleton below.
    
    XXX TODO: Check that the 'on_what' argument is already saved when calling this!
    """
    def _notify(self, publisher, who, did_what, on_who = None, on_what = None):
        """
        Send the notification
        """
        from twistranet.core.models import Notification
        from twistranet.core.models.account import SystemAccount
        __account__ = SystemAccount.objects.get()
        l = Notification(
            publisher = publisher,
            who = who,
            did_what = did_what,
            on_who = on_who,
            on_what = on_what,
            permissions = "public",
        )
        l.save()
        return l
    
    def joined(self, account, community):
        return self._notify(
            publisher = community,
            who = account,
            did_what = "joined",
            on_who = community,
        )

    def likes(self, account, content):
        """
        Say an account likes the given object.
        """
        return self._notify(
            publisher = account,
            who = account,
            did_what = "likes",
            on_what = content,
        )

notifier = Notifier()
