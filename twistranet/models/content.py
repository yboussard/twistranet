from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from account import Account

class ContentRegistryManager:
    """
    Content registry for content types.
    Maybe we should find some better way to register content,
    to avoid calling ContentRegistry.register(...)
    """
    # This holds a classname: (model, form) dictionnary
    _registry_ = {}
    
    def register(self, model_class, form_class):
        """
        Register a model class into the TwistraNet application.
        Will bind the form to the model.
        XXX TODO: Provide a way of ordering forms?
        """
        self._registry_[model_class.__name__]  = (model_class, form_class, )
    
    
    def getContentFormClasses(self, user_account, wall_account):
        """
        This method returns the appropriate content forms for a user seeing an account page.
        This returns a list of Form classes
        """
        # XXX Temporary. Should perform security checks one day ;)
        return [ r[1] for r in self._registry_.values() ]
        
    
ContentRegistry = ContentRegistryManager()
    

class ContentManager(models.Manager):
    """
    This manager is used for secured content (via the secured()) method.
    Methods are useable if the _account attribute is set.
    """

    

class PublicContentManager(ContentManager):
    """
    This manager used for content only fetches strictly public content.
    XXX TODO !!!
    """
    def get_query_set(self):
        # XXX TODO: Filter only public content
        return super(PublicContentManager, self).get_query_set().filter(text = "qlmkdsfjqmlksdjq")


class Content(models.Model):
    """
    Abstract content representation class.
    
    API warriors: always use the getFiltered(account) method to fetch content for a given account.
    When you use the 'objects' manager, only PUBLIC content is retrieved.
    
    The _unsecured manager is the only way of accessing all objects, but never use it in your app.
    """
    # Usual metadata
    date = models.DateTimeField(auto_now = True)
    content_type = models.TextField()
    author = models.ForeignKey(Account, related_name = "by")    # The original author account, 
                                                                # not necessarily the diffuser (esp. for auto producers or communities)

    # The default text displayed for this content
    text = models.TextField()
    
    # Security stuff
    diffuser = models.ForeignKey(Account)
    public = models.BooleanField()          # If false, reader must be approved for the diffuser to access it
    
    # Custom Managers. Never never never use the __unsecured manager!
    objects = PublicContentManager()
    __unsecured = ContentManager()
    
    def __unicode__(self):
        return "Content %d of type %s" % (self.id, self.content_type, )
    
    class Meta:
        app_label = 'twistranet'

    def getText(self):
        """
        Override this to not use the 'text' attribute of the super class
        """
        return self.text

    def preSave(self, account):
        """
        Populate special content information before saving it.
        XXX TODO: Use a trigger to automate this!
        """
        self.content_type = self.__class__.__name__
        self.author = account
        self.diffuser = account
    
    def getFiltered(self, account):
        """
        Return a query set holding only visible content for a given account.
        """
        # my_followed = account.getMyFollowed()
        my_network = account.getMyNetwork()
        return self.__unsecured.filter(
            (
                # Public stuff by the people I follow
                Q(public = True)
            ) | (
                # Public AND private stuff from the people in my network
                Q(diffuser__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = account)
            )
        )
        filtered._account = account
    filtered = classmethod(getFiltered)
        
    
    def getFollowedContent(self, account):
        """
        Return content that is specifically address to the given account,
        ie. content the account actually follows.
        """
        my_followed = account.getMyFollowed()
        my_network = account.getMyNetwork()
        return self.__unsecured.filter(
            (
                # Public stuff by the people I follow
                Q(diffuser__in = my_followed) & Q(public = True)
            ) | (
                # Public AND private stuff from the people in my network
                Q(diffuser__in = my_network)
            ) | (
                # And, of course, what I wrote !
                Q(author = account)
            )
        )
    followed = classmethod(getFollowedContent)

    
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
