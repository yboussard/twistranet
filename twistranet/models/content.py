from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import basemanager 
from account import Account
from scope import *

class ContentManager(basemanager.BaseManager):
    """
    This manager is used for secured content (via the secured()) method.
    Methods are useable if the _account attribute is set.
    """
    def get_query_set(self):
        """
        Return a queryset of 100%-authorized objects.
        """
        # Check for anonymous query
        authenticated = self._getAuthenticatedAccount()
        base_query_set = super(ContentManager, self).get_query_set()
        if not authenticated:
            # TODO: Return anonymous objects
            return base_query_set.filter(
                scope = CONTENTSCOPE_PUBLIC,
                publisher__scope = ACCOUNTSCOPE_ANONYMOUS,
                )

        # System account: return all objects
        if authenticated.account_type == "SystemAccount":
            authenticated.systemaccount   # This is one more security check, will raise if DB is not properly set
            return base_query_set  # The base qset with no filter

        # Return all content objects I can reach
        my_network = authenticated.getMyNetwork()
        return base_query_set.filter(
            (
                # Public stuff
                # XXX TODO: Add publisher visibility check
                Q(scope = CONTENTSCOPE_PUBLIC)
            ) | (
                # Stuff from the people in my network
                Q(scope__in = (CONTENTSCOPE_PUBLIC, CONTENTSCOPE_NETWORK), publisher__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = authenticated)
            )
        ).distinct()
        
    def getAuthorized(self, account = None):
        """
        Return content authorized for the given account.
        If account is None, use currently auth user (and should be the same that get_query_set)
        """
        # Get proper account treatment
        if not account:
            return self.get_query_set()
            
        base_query_set = self.get_query_set()

        # System account: return all possible objects
        if account.account_type == "SystemAccount":
            return base_query_set  # The base qset with no filter

        # Return all content objects the account can reach
        my_network = account.getMyNetwork()
        return base_query_set.filter(
            (
                # Public stuff
                # XXX TODO: Add publisher visibility check
                Q(scope = CONTENTSCOPE_PUBLIC)
            ) | (
                # Stuff from the people in my network
                Q(scope__in = (CONTENTSCOPE_PUBLIC, CONTENTSCOPE_NETWORK), publisher__in = my_network)
            ) | (
                # And, of course, what he wrote !
                Q(author = account)
            )
        ).distinct()
        
    
    def getFollowed(self, account = None):
        """
        Return a queryset of objects the account follows.
        You can specify another account (useful for a wall display for example)
        """
        if not account:
            account = self._getAuthenticatedAccount()        
        my_followed = account.getMyFollowed()
        my_network = account.getMyNetwork()
        
        return self.get_query_set().filter(
            (
                # Public stuff by the people I follow
                Q(publisher__in = my_followed, scope__in = (CONTENTSCOPE_PUBLIC, CONTENTSCOPE_NETWORK))
            ) | (
                # Public AND private stuff from the people in my network
                Q(publisher__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = account)
            )
        ).distinct().order_by("-date")
        
        

    
class Content(models.Model):
    """
    Abstract content representation class.
    
    API warriors: always use the getFiltered(account) method to fetch content for a given account.
    When you use the 'objects' manager, only PUBLIC content is retrieved.
    
    The _objects manager is the only way of accessing all objects, but never use it in your app.
    You'll usually call methods from the ContentFromAccountMixin class to access content objects.
    """
    # Usual metadata
    date = models.DateTimeField(auto_now = True)
    content_type = models.TextField()
    author = models.ForeignKey(Account, related_name = "by")    # The original author account, 
                                                                # not necessarily the publisher (esp. for auto producers or communities)

    # The default text displayed for this content
    text = models.TextField()
    
    # Security stuff
    publisher = models.ForeignKey(Account)   # The account this content is published for.
    scope = models.CharField(max_length = 16, choices = CONTENT_SCOPES, default = CONTENTSCOPE_PUBLIC)
    objects = ContentManager()
    
    def __unicode__(self):
        return "%s %d by %s" % (self.content_type, self.id, self.author)
    
    class Meta:
        app_label = 'twistranet'

    def getText(self):
        """
        Override this to not use the 'text' attribute of the super class
        """
        return self.text

    @property
    def subclass(self):
        """
        Return the exact subclass this object belongs to.
        Use this to display it.
        """
        obj = getattr(self, self.content_type.lower())
        return obj
        
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        if self.scope not in CONTENT_SCOPE_IDS:
            raise ValidationError("Invalid content scope: '%s'" % self.scope)
        self.content_type = self.__class__.__name__
        if self.content_type == Content.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")

        # Check content edition
        authenticated = Content.objects._getAuthenticatedAccount()
        if not authenticated:
            raise ValidationError("You can't save a content anonymously.")
        if self.author_id is None:
            self.author = authenticated
        else:
            if self.author != authenticated:
                raise RuntimeError("You're not allowed to edit this content.")
                
        if self.publisher_id is None:
            self.publisher = self.author
        return super(Content, self).save(*args, **kw)


class StatusUpdate(Content):
    """
    StatusUpdate is the most simple content available (except maybe helloworld).
    It provides a good example of what you can do with a content type.
    """
    class Meta:
        app_label = 'twistranet'

    
class Link(Content):
    class Meta:
        app_label = 'twistranet'
    
    
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
