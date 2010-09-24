from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Account(models.Model):
    """
    A generic account.
    This is an abstract class.
    Can be subclassed as a user account, group account, app account, etc
    """
    # XXX Should hold:
    # An unique ID
    # A picture
    # A friendly name
    # name = models.CharField(max_length = 127)
    account_type = models.CharField(max_length = 64)

    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        if self.__class__ == Account.__name__:
            raise RuntimeError("You can't directly save an account object.")
        self.account_type = self.__class__.__name__
        super(Account, self).save(*args, **kw)
    
    @property
    def fullname(self,):
        if self.account_type == "UserAccount":
            return self.useraccount.user.username
        else:
            return self.id
        
    
    def __unicode__(self):
        return u"%s: %s" % (self.account_type, self.fullname, )

    class Meta:
        app_label = 'twistranet'

    def getMyFollowed(self):
        """
        Return list of followed persons (ie. approval not set)
        """
        return Account.objects.filter(target_whose__initiator = self, target_whose__approved = False)
        
    def getMyFollowers(self):
        """
        Return list of people who follow me (ie. I didn't approve)
        """
        return Account.objects.filter(initiator_whose__target = self, initiator_whose__approved = False)

    def getMyNetwork(self):
        """
        Return list of my networked (ie. approved) people
        """
        # Both calls must return the same (normally...)
        return Account.objects.filter(initiator_whose__target = self, initiator_whose__approved = True)
        return Account.objects.filter(target_whose__initiator = self, target_whose__approved = True)
 
    @property
    def content(self):
        """
        return bound content mgr
        """
        from contentwrapper import ContentWrapper
        return ContentWrapper(self)
        
    @property
    def communities(self):
        """
        Return communities authorized for this account
        """
        from communitywrapper import CommunityWrapper
        return CommunityWrapper(self)
        
class SystemAccount(Account):
    """
    The system accounts for TwistraNet.
    There must be at least 1 system account called '_system'. It's its role to build initial content.
    System accounts can reach ALL content from ALL communities.
    """
    class Meta:
        app_label = "twistranet"
    
    @staticmethod
    def getSystemAccount():
        """Return main (and only) system account"""
        return SystemAccount.objects.all()[0]       # REVIEW - consider .get method ; [0] is not error safe ; you don't trap exception here
        
class UserAccount(Account):
    """
    Generic User account.
    This holds user profile as well!
    """
    user = models.OneToOneField(User, unique=True, related_name = "useraccount")

    def __unicode__(self):
        return self.useraccount.user.username

    class Meta:
        app_label = 'twistranet'


