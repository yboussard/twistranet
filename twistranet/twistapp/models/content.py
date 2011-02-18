from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import html, translation
import twistable
from account import Account
from resource import Resource
from twistranet.twistapp.lib import roles, permissions
from twistranet.twistapp.signals import *

class ContentManager(twistable.TwistableManager):
    """
    This manager is used for secured content (via the secured()) method.
    Methods are useable if the _account attribute is set.
    
    For performance reasons, it's UP TO YOU to call the distinct() method.
    """            
    def getActivityFeed(self, account):
        """
        Return activity feed content for the given account
        It's content the account follows + content it produced + log messages he's the originator
        """
        return self.filter(
            Q(publisher = account) | Q(owner = account)
        ).exclude(model_name = "Comment").distinct()
            
    
    def get_follow_filter(self, account = None):
        """
        Return the filter specifying how to follow the given account.
        If account is specified, we ensure that returned content is visible by the given account.
        """
        auth = self._getAuthenticatedAccount()
        if account is None:
            account = auth
        
        return (Q(
            publisher__requesting_network__client__id = account.id,
        ) | Q(
            publisher__id = account.id,
        ))
            
    @property
    def followed(self):
        """
        Followed content by currently auth user. Used to display frontpage.
        Followed content is content:
        - that is published on ppl or communities in my network ;
        - my own content ;
        """
        return self.filter(self.get_follow_filter()).distinct()
                        

class _AbstractContent(twistable.Twistable):
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
    
    If you want to create your own text-based content type, just add a text = models.TextField() line in your subclass.
    """
    # Resources associated to this content
    resources = models.ManyToManyField(Resource, blank = True, null = True, db_index = True)
    
    # This points to the original version of a translated content.
    # (Not implemented yet, but will be one day.)
    translation_of = models.ForeignKey(
        "Content",
        related_name = "translated_versions",
        null = True,
        blank = True,
        db_index = True
    )
    
    # Security models available for the user
    permission_templates = permissions.content_templates
    
    # This is used to identify comment-derivated objects
    @property
    def is_comment(self,):
        from twistranet.content_types.models import Comment
        return issubclass(self.model_class, Comment)
    
    # View overriding support. Not very DRYful but convenient for product authors.
    # Just overload the 'type_summary_view' in your subclasses if you want.
    # Same for detail_view. 
    # If you don't want implicit links to detail view, set type_detail_link to False.
    # This is useful for status updates: we don't want links everywhere to status updates,
    # but want to be able to reference them anyway.
    # Use those variables when setting information, but ALWAYS use the 'type_'-less property
    # when accessing it: that will avoid an unncecessary database hit.
    type_summary_view = "content/summary.part.html"
    type_detail_view = "content/view.html"
    type_detail_link = True
    type_text_template_creation = "email/created_content.txt"
    type_html_template_creation = "email/created_content.html"
    default_picture_resource_slug = "default_menu_picture"
    
    @property
    def detail_link(self,):
        return self.model_class.type_detail_link
        
    class Meta:
        app_label = 'twistapp'

    #                                                               #
    #                   Content internal stuff                      #
    #                                                               #
    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        See Content class documentation for more information on that.
        """
        # Don't allow direct Content object saving
        if self.__class__ == Content:
            raise RuntimeError("You're not allowed to directly save a Content object. Use your actual content type instead.")
        
        # Confirm publishing rights
        authenticated = Content.objects._getAuthenticatedAccount()
        if not authenticated:
            raise PermissionDenied("Anonymous user can't publish anything.")
        if self.publisher_id is None:
            if not authenticated.can_publish:
                raise PermissionDenied("%s can't publish anything." % (authenticated, ))
        else:
            if not self.publisher.can_publish:
                raise PermissionDenied("%s can't publish on %s." % (authenticated, self.publisher, ))

        # Creation or not?
        creation = not self.id
        
        # Check if user has modification rights for existing content
        if creation:
            if not self.can_edit:
                raise PermissionDenied("You're not allowed to edit this content.")
                        
        # Actually save stuff
        ret = super(Content, self).save(*args, **kw)
        
        # If we're on a creation mode, send the proper signal and return.
        # Here we determine who has to be notified about this content.
        # To be notified for a content, a UserAccount must...
        #   - have view access to the content (for sure)
        #   - either:
        #       - be the publisher of the content ; (ie. content posted on my wall)
        #       - be a member of the publisher ;    (ie. content published on a community)
        #   The comments have one more rule : all the parents that are not in this list are notified
        #   (but this is treated in the Comment class).
        if creation:
            listeners = self.listeners
            if listeners:
                content_created.send(
                    sender = self.__class__, 
                    instance = self, 
                    target = self.listeners,
                    text_template = self.model_class.type_text_template_creation,
                    html_template = self.model_class.type_html_template_creation,
                )
        return ret

    @property
    def listeners(self,):
        """
        List of ppl who will get notified when this content is created.
        # To be notified for a content, a UserAccount must...
        #   - have view access to the content (for sure)
        #   - either:
        #       - be the publisher of the content ; (ie. content posted on my wall)
        #       - be a member of the publisher ;    (ie. content published on a community)

        One day we'll implement explicit content following.
        """
        from twistranet.twistapp.models import Community
        pub = self.publisher
        owner = self.owner
        if pub.id == owner.id:
            return []       # I won't get notified for content I create!
        if issubclass(pub.model_class, Community):
            # Notify everybody in the community but the content author
            return pub.object.members.exclude(id = owner.id)
        return [ pub ]

    def delete(self,):
        """
        Delete object after we've checked security
        """
        if self.id:
            if not self.can_delete:
                raise PermissionDenied("You're not allowed to delete this object.")
        return super(Content, self).delete()
        
    #                                                                   #
    #                       Display specificities                       #
    #                                                                   #
    
    def owner_for_display(self):
        """
        Get the owner that's going to be said the post author.
        General case: same as self.owner, except for communities,
        where any community member acts for its "spokeperson"

        XXX TODO: Cache most of this at creation-time!
        """
        _c = getattr(self, '_c_owner_for_display', None)
        if _c:
            return _c
        from community import Community
        from account import SystemAccount
        display = self.owner
        if issubclass(self.owner.model_class, SystemAccount):
            if self.publisher:
                display = self.publisher
        if issubclass(self.publisher.model_class, Community):
            if self.publisher.community.isMember(self.owner):
                display = self.publisher
        setattr(self, '_c_owner_for_display', display)
        return display

