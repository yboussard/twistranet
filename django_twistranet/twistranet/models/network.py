from django.db import models
from django.contrib.auth.models import User
from django_twistranet.twistranet.models import Content
from django_twistranet.twistranet.models import Account


class NetworkManager(object):
    """
    Set of methods to handle relations and cache them
    XXX TODO with pickling and replace Account & Community methods
    """
    

class Network(models.Model):
    """
    A relation describes what happens when two users 'meet'.
    Kind of relations :
    - Follow (asymetrical relation w/o approval)
    - Network (symetrical relation w/ approval implied)
    The initiator (client) is always ok for accepting the target (of course).
    
    To find the accounts a user has been authorized to access, do:
    - in a query:
        Account.objects.filter(targeted_network__target = account)
    - with an object:
        account.requesting_accounts.all()
    
    To find the accounts a user has requested access to, do:
    - in a query:
        Account.objects.filter(requesting_network.client = account)
    - within an object:
        account.targeted_accounts.all()
        
    To find if 'admin' has been accepted to a's nwk:
    - in a query:
        Account.objects.filter(targeted_network__target = admin, targeted_network__client = a)
    - within an object:
        admin.requesting_accounts.filter(targeted_network__client__id = a.id)
    
    Then, to find the 100% accepted network, you can do:
    - in a query:
        Account.objects.filter(
            targeted_network.target = account,
            requesting_network.client = account,
            )
    - within an object:
        account.targeted_accounts.filter(targeted_network__target = account)
        
    An account is (often) pre-loaded with its targeted_accounts, so that the # of queries is lowered.
    Remember that an account has more chance to have LESS targeted_accounts than requesting_accounts
    (think about communities vs. users).
    
    
    Consider A, B relations. A <=> B. There are 4 possible queries:
    
    UserAccount.objects.filter(publisher__targeted_network__client__id = B.id)   =>   Return B from the B => A relation
    UserAccount.objects.filter(publisher__requesting_network__client__id = B.id)   =>   Return A from the B => A relation
    UserAccount.objects.filter(publisher__targeted_network__target__id = B.id)   =>   Return A from the A => B relation
    UserAccount.objects.filter(publisher__requesting_network__target__id = B.id)   =>   Return B from the A => B relation
    
    To return content published by ppl & communities in my network, do the contrary:
    Content.objects.filter(publisher__targeted_network__client__id = <myaccount.id>)
    
    """
    client = models.ForeignKey(Account, related_name = "targeted_network")
    target = models.ForeignKey(Account, related_name = "requesting_network")
    is_manager = models.BooleanField(default = False)       # True if the client has acquired a management role on the target. Only for communities.
    
    def __unicode__(self):
        return u"%s => %s (mgr=%s)" % (self.client, self.target, self.is_manager, )

    class Meta:
        app_label = 'twistranet'
        unique_together = ("client", "target", )



