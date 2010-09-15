from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from TwistraNet.account.models import Account


class Content(models.Model):
    """
    Abstract content representation class.
    """
    # Usual metadata
    date = models.DateTimeField(auto_now = True)
    content_type = models.TextField()
    author = models.ForeignKey(User)        # Informative; diffuser is what's interesting there

    # The default text displayed for this content
    text = models.TextField()
    
    # Security stuff
    diffuser = models.ForeignKey(Account)
    public = models.BooleanField()          # If false, reader must be approved for the diffuser to access it

    def getText(self):
        """
        Override this to not use the 'text' attribute of the super class
        """
        return self.text

    
    def preSave(self, account):
        """
        Populate special content information before saving it.
        """
        self.content_type = self.__class__.__name__
        self.author = account.user
        self.diffuser = account
        self.public = True
    
    # Shortcut for the 'secured' wrapper
    def secured(self, account):
        """
        Return a pre-filtered list of objects available for given user account.
        This is where the main security stuff happens and this is THE QUERY TO OPTIMIZE!
        """
        my_followed = account.getMyFollowed()
        my_network = account.getMyNetwork()
        return self.objects.filter(
            (
                # Public stuff by the people I follow
                Q(diffuser__in = my_followed) & Q(public = True)
            ) | (
                # Public AND private stuff from the people in my network
                Q(diffuser__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = account.user)
            )
        )
        
    secured = classmethod(secured)

    
class StatusUpdate(Content):
    """
    StatusUpdate is the most simple content available (except maybe helloworld).
    It provides a good example of what you can do with a content type.
    """
    pass
    
    
class Link(Content):
    pass
    
    
class File(Content):
    """
    Abstract class which represents a File in database.
    We just add filename information plus several methods to display it.
    """
    
class Image(File):
    """
    Image file
    """
    
class Video(File):
    """
    Video content
    """
    
class Comment(Content):
    """
    Special comment handling. Comment is 'just' a special type of content.
    Comments are not commentable themselves...
    """
