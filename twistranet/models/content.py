from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
import basemanager 
from account import Account
from resource import Resource
from twistranet.lib import roles, permissions, languages


class ContentManager(basemanager.BaseManager):
    """
    This manager is used for secured content (via the secured()) method.
    Methods are useable if the _account attribute is set.
    
    For performance reasons, it's UP TO YOU to call the distinct() method.
    """
    def get_query_set(self):
        """
        Return a queryset of 100%-authorized objects.
        """
        # Check for anonymous query
        authenticated = self._getAuthenticatedAccount()
        base_query_set = super(ContentManager, self).get_query_set()
        if not authenticated:
            # If global community is restricted, don't return anything
            if not Account.objects.filter(account_type = "GlobalCommunity"):
                return base_query_set.filter(id = -1)       # An on-purpose invalid filter
            
            # Return anonymous objects if global community is listable to anonymous.
            # XXX TODO: Avoid the distinct method
            return base_query_set.filter(
                _permissions__name = permissions.can_view,
                _permissions__role__in = roles.content_public.implied(),
                publisher___permissions__name = permissions.can_view,
                publisher___permissions__role__in = (roles.anonymous, ),
                ).distinct()
        
        # System account: return all objects
        if authenticated.account_type == "SystemAccount":
            authenticated.systemaccount     # This is one more security check, will raise if DB is not properly set
            return base_query_set           # The base qset with no filter
        
        # XXX TODO: Avoid the distinct method
        return base_query_set.filter(self._getViewFilter(authenticated)).distinct()
        
        
    def getActivityFeed(self, account):
        """
        Return activity feed content for the given account
        It's content the account follows + content it produced + log messages he's the originator
        """
        return self.filter(
            Q(publisher = account) | Q(author = account) | Q(logmessage__who = account) | Q(logmessage__on_who = account)
            ).distinct()
        
    
    def _getViewFilter(self, account):
        """
        Get main security filter parameter. Send this to the filter() method of a queryset.
        This will behave normally, ie. will not shortcut SystemAccount stuff.
        """
        # Return all content objects I can reach
        my_network = account.network
        my_communities = account.communities
        communities_i_manage = () # XXX TODO
        # account.communities.filter(
        #             membership_manager__member = account,
        #             membership_manager__is_manager = True,
        #             )
        
        return (
            # Public stuff, ie. stuff I can view if I can view the publisher
            Q(
                _permissions__name = permissions.can_view,
                _permissions__role__in = roles.content_public.implied(),
                publisher___permissions__name = permissions.can_view,
                publisher___permissions__role__in = roles.authenticated.implied(),
            )
        ) | (
            # Stuff from the people in my network
            Q(
                publisher__in = my_network,
                _permissions__name = permissions.can_view,
                _permissions__role__in = roles.content_network.implied() + roles.content_public.implied(),
                publisher___permissions__name = permissions.can_view,
                publisher___permissions__role__in = roles.account_network.implied(),
            )
        ) | (
            # Stuff from the communities I'm in
            Q(
                publisher__in = my_communities,
                _permissions__name = permissions.can_view,
                _permissions__role__in = roles.content_community_member.implied() + roles.content_public.implied(),
                publisher___permissions__name = permissions.can_view,
                publisher___permissions__role__in = roles.community_member.implied(),
            )
        ) | (
            # Stuff from the communities I manage
            Q(
                publisher__in = communities_i_manage,
                _permissions__name = permissions.can_view,
                _permissions__role__in = roles.content_community_manager.implied() + roles.content_public.implied(),
                publisher___permissions__name = permissions.can_view,
                publisher___permissions__role__in = roles.community_manager.implied(),
            )
        ) | (
            # And, of course, what I wrote !
            Q(
                author = account,
            )
        )
    
    def getViewableBy(self, account):
        """
        Get content the given account can view.
        This will not return content that is not viewable by authenticated user (of course).
        """
        return self.get_query_set().filter(self._getViewFilter(account))
    
    @property
    def followed(self):
        """
        Followed content by currently auth user
        """
        account = self._getAuthenticatedAccount()
        return self.filter(self._getFollowFilter(account)).distinct()
        
    def _getFollowFilter(self, account):
        """
        Return the filter parameter set to follow an account.
        """
        # Return stuff exclusively from people / communities I'm interested in
        my_relations = account.my_interest
        return Q(publisher__in = my_relations) | Q(publisher = account) | Q(author = account)
        
        
    def getFollowedBy(self, account):
        """
        Return a queryset of objects the account follows.
        You can specify another account for a wall display for example.
        If you want to see current user's followed stuff, use self.followed pty instead.
        """
        return self.filter(
                self._getViewFilter(account)
            ).filter(
                self._getFollowFilter(account)
            ).distinct()
        

class _AbstractContent(models.Model):
    """
    We use this to enforce using our manager on subclasses.
    This way, we avoid enforcing you to re-declare objects = ContentManager() on each content class!
    
    See: http://docs.djangoproject.com/en/1.2/topics/db/managers/#custom-managers-and-model-inheritance
    """
    class Meta:
        abstract = True

    # Our security model
    objects = ContentManager()


class Content(_AbstractContent):
    """
    Abstract content representation class.
    """
    # The publisher this content is published for
    publisher = models.ForeignKey(Account)                      # The account this content is published for.

    # Usual metadata
    created_at = models.DateTimeField(auto_now = True)
    content_type = models.TextField()
    author = models.ForeignKey(Account, related_name = "by")    # The original author account, 
                                                                # not necessarily the publisher (esp. for auto producers or communities)

    # The default text displayed for this content
    text = models.TextField()
    
    # Resources associated to this content
    resources = models.ManyToManyField(Resource)
    
    # XXX TODO: Implement sources (ie. the client this 'tweet' is coming from)
    source = "web"
    
    # I18N support
    language = models.CharField(
        max_length = 10,
        blank = True,
        choices = languages.available_languages,
        default = languages.available_languages[0][0],
        )
    translation_of = models.ForeignKey(
        "Content",
        related_name = "translations",
        null = True,
        blank = True,
        )
    
    # Security models available for the user
    # XXX TODO: Use a foreign key instead with some clever checking, or, better create a new field type.
    permission_templates = permissions.content_templates
    permissions = models.CharField(
        max_length = 32, 
        choices = permissions.content_templates.get_choices(), 
        default = permissions.content_templates.get_default(),
        )
        
    # View overriding support
    # XXX TODO: Find a way to optimize this without having to query the underlying object
    summary_view = "content/summary.part.html"
    
    is_content = True
    
    def __unicode__(self):
        return "%s %d by %s" % (self.content_type, self.id, self.author)
    
    class Meta:
        app_label = 'twistranet'

    #                                                               #
    #                       Display management                      #
    # You can override this in your content types.                  #
    #                                                               #

    def getText(self):
        """
        Override this to not use the 'text' attribute of the super class
        """
        return self.text
        
    @property
    def headline(self):
        """
        Use this to display the headline on your activity feed.
        You can have some logic to display a different headline according to the content's properties.
        
        Default is to display the 255 first characters of the raw text content in other cases.
        """
        text = self.getText()
        if len(text) < 255:
            return text
        return u"%s [...]" % text[:255]
    
    @property
    def summary(self):
        """
        Inner summary text. Return properly-formated HTML summary.
        Default is to display nothing if text is the same as the headline.
        """
        if self.getText() == self.headline:
            return None
        return self.getText()
        
    #                                                               #
    #                       Security Management                     #
    #                                                               #
    
    @property
    def can_list(self):
        """
        Same as can_view for content objects?
        XXX TODO: Clean that a little bit?
        """
        auth = Account.objects._getAuthenticatedAccount()
        return auth.has_permission(permissions.can_view, self)

    #                                                               #
    #                   Content internal stuff                      #
    #                                                               #

    @property
    def model_class(self):
        """
        Return the subobject model class
        """
        from twistranet.models import contentregistry
        return contentregistry.ContentRegistry.getModelClass(self.content_type)

    @property
    def object(self):
        """
        Return the exact subclass this object belongs to.
        Use this to display it.
        
        XXX TODO: Make this more consistant with account
        """
        obj = getattr(self, self.content_type.lower())
        return obj
        
    @property
    def permissions_list(self):
        import _permissionmapping
        return _permissionmapping._ContentPermissionMapping.objects._get_detail(self.id)
        
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        """
        import _permissionmapping
        
        # Confirm publishing rights
        authenticated = Content.objects._getAuthenticatedAccount()
        if self.publisher_id is None:
            if not authenticated.can_publish:
                raise RuntimeError("%s can't publish anything." % (authenticated, ))
        else:
            if not self.publisher.can_publish:
                raise RuntimeError("%s can't publish on %s." % (authenticated, self.publisher, ))
        
        # XXX TODO: Check permission template first?
        if self.__class__.__name__ == Content.__name__:
            raise ValidationError("You cannot save a raw content object. Use a derived class instead.")
        self.content_type = self.__class__.__name__

        # Check if I have content edition rights
        # XXX Have to use a decorator instead
        if not authenticated:
            raise ValidationError("You can't save a content anonymously.")
        if self.author_id is None:
            self.author = authenticated
        else:
            if self.author != authenticated:
                raise RuntimeError("You're not allowed to edit this content.")
                
        # Set publisher
        if self.publisher_id is None:
            self.publisher = self.author

        # Actually saves stuff
        ret = super(Content, self).save(*args, **kw)
        
        # Set/reset permissions. We do it last to be sure we've got an id.
        _permissionmapping._ContentPermissionMapping.objects._applyPermissionsTemplate(self, _permissionmapping._ContentPermissionMapping)
        return ret


    def delete(self,):
        """
        Delete object after we've checked security
        """
        authenticated = Content.objects._getAuthenticatedAccount()
        if not authenticated.has_permission(permissions.can_delete, self):
            raise PermissionDenied("You're not allowed to delete this object.")
        return super(Content, self).delete()

class StatusUpdate(Content):
    """
    StatusUpdate is the most simple content available (except maybe helloworld).
    It provides a good example of what you can do with a content type.
    """
    class Meta:
        app_label = 'twistranet'

class LogMessage(Content):
    """
    ACCOUNT did WHAT [on ACCOUNT/CONTENT].
    This is an internal system message, available to people following either the first or second mentionned account.
    It's meant to be posted by SystemAccount only.
    
    Author is usually SystemAccount.
    Publisher is usually the community (or account) this content belongs to.
    """
    # Defined fields on the logmessage
    who = models.ForeignKey(Account, related_name = "who")
    did_what = models.CharField(
        max_length = 32, 
        choices = (
            ("joined", "joined", ),
            ("left", "left", ),
            ("picture", "changed his/her profile picture", ),
            ("network", "is connected to", ),
            ("follows", "follows", ),
            ("likes", "likes", ),
            ),
        )
    on_who = models.ForeignKey(Account, related_name = "on_who", null = True)
    on_what = models.ForeignKey(Content, related_name = "on_what", null = True)
    
    # View overriding support
    summary_view = "content/summary.logmessage.part.html"
    
    def __unicode__(self,):
        return u"LogMessage %d: %s" % (self.id, self.getText())
    
    def getText(self):
        """
        XXX TODO: Translate the sentence using gettext!
        """
        from django.core.urlresolvers import reverse
        who_url = reverse('twistranet.views.account_by_id', args = (self.who.id,))
        if self.on_who:
            on_who_url = reverse('twistranet.views.account_by_id', args = (self.on_who.id,))
            return "<a href='%s'>%s</a> %s <a href='%s'>%s</a>" % (who_url, self.who, self.did_what, on_who_url, self.on_who)
        elif self.on_what:
            on_what_url = reverse('twistranet.views.content_by_id', args = (self.on_what.id,))
            return "<a href='%s'>%s</a> %s <a href='%s'>%s</a>" % (who_url, self.who, self.did_what, on_what_url, self.on_what)
        else:
            return "<a href='%s'>%s</a> %s" % (who_url, self.who, )
    
    class Meta:
        app_label = "twistranet"
    
class Link(Content):
    class Meta:
        app_label = 'twistranet'
    
class File(Content):
    """
    Abstract class which represents a File in database.
    We just add filename information plus several methods to display it.
    """
    class Meta:
        app_label = 'twistranet'
    
class Image(File):
    """
    Image file
    """
    class Meta:
        app_label = 'twistranet'
    
    
class Video(File):
    """
    Video content
    """
    class Meta:
        app_label = 'twistranet'

    
class Comment(Content):
    """
    Special comment handling. Comment is 'just' a special type of content.
    Comments are not commentable themselves...
    """
    class Meta:
        app_label = 'twistranet'
    
