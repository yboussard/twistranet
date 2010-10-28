"""
TwistraNet internal notifications system.
We use this to log short status message about what people do in TN.
"""

class Notifier(object):
    """
    Helper stateless class to manage notifications for various actions.
    Use the 'notifier' singleton below.
    """
    def joined(self, account, community):
        from twistranet.models import Notification
        from twistranet.models.account import SystemAccount
        __account__ = SystemAccount.objects.get()
        l = Notification(
            publisher = community,
            who = account,
            did_what = "joined",
            on_who = community,
            permissions = "public",
            )
        l.save()


notifier = Notifier()
