"""
TwistraNet internal log system.
We use this to log short status message about what people do in TN.
"""


def joined(account, community):
    from twistranet.models import content
    from twistranet.models.account import SystemAccount
    __account__ = SystemAccount.objects.get()
    l = content.LogMessage(
        publisher = community,
        who = account,
        did_what = "joined",
        on_who = community,
        permissions = "public",
        )
    l.save()

