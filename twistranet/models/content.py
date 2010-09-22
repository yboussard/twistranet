from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from account import Account

CONTENT_SCOPES = (
    ("public",      "This content is visible by anyone who has access to the publisher.", ),
    ("network",     "This content is visible only by the publisher's network.", ),
    ("private",     "This content is private, only the author can see it.", ),
)

CONTENT_SCOPE_IDS = [ t[0] for t in CONTENT_SCOPES ]

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
        
    def getModelClass(self, name):
        """
        Evident :)
        """
        return self._registry_[name][0]
        
    
ContentRegistry = ContentRegistryManager()
    

class ContentManager(models.Manager):
    """
    This manager is used for secured content (via the secured()) method.
    Methods are useable if the _account attribute is set.
    """
    def get_query_set(self):
        return super(ContentManager, self).get_query_set().order_by("-date")
    

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
    scope = models.CharField(max_length = 16, choices = CONTENT_SCOPES, default = CONTENT_SCOPES[0])
    _bound = False          # True if content is secured with a correct account
        
    # Custom Managers. Never never never use the __unsecured manager!
    # You should not use managers from your subclasses (they will return Content objects instead of your class objects)
    objects = PublicContentManager()
    _unsecured = ContentManager()
    
    def __unicode__(self):
        return "%s %d by %s" % (self.content_type, self.id, self.author)
    
    class Meta:
        app_label = 'twistranet'

    def getText(self):
        """
        Override this to not use the 'text' attribute of the super class
        """
        return self.text

    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        if self.scope not in CONTENT_SCOPE_IDS:
            raise ValidationError("Invalid community scope: '%s'" % self.scope)
        self.content_type = self.__class__.__name__
        if self.content_type == Content.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
        if self.author_id is None or not self._bound:
            raise ValidationError("Content author must be set before saving this. You should either use account.content.create() or content.bound() methods to set it.")
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
