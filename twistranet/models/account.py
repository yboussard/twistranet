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

    class Meta:
        app_label = 'twistranet'

    def __unicode__(self):
        return self.useraccount.user.username

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
        Return the queryset representing content available for this user.
        """
        from content import Content
        return Content.filtered(self)
    
    @property
    def followed_content(self):
        """
        Return the queryset representing content specifically followed by this user.
        """
        from content import Content
        return Content.followed(self)
        

class UserAccount(Account):
    """
    Generic User account.
    This holds user profile as well!
    """
    user = models.OneToOneField(User, unique=True, related_name = "account")

    class Meta:
        app_label = 'twistranet'


