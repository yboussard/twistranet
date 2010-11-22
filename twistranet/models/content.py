from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import html, translation
import twistable
from account import Account
from resource import Resource
from twistranet.lib import roles, permissions, languages, utils

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
            Q(publisher = account) | Q(owner = account) | Q(notification__who = account) | Q(notification__on_who = account)
        ).distinct()
            
    
    def get_follow_filter(self, account = None):
        """
        Return the filter specifying how to follow the given account.
        If account is specified, we ensure that returned content is visible by the given account.
        """
        if account is None:
            account = self._getAuthenticatedAccount()
        
        return (Q(
            publisher__targeted_network__target__id = account.id,
        ) | Q(
            publisher__id = account.id,
        )) & (
            twistable.Twistable.objects.get_anonymous_filter(account) | \
            twistable.Twistable.objects.get_public_filter(account) | \
            twistable.Twistable.objects.get_network_filter(account) | \
            twistable.Twistable.objects.get_owner_filter(account)
        )
            
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
    # The publisher this content is published for
    # publisher = models.ForeignKey(Account)                      # The account this content is published for.
    

    # Usual metadata
    # Text representation of this content
    # Usually content is represented that way:
    # (pict) HEADLINE
    # Summary summary summary [Read more]
    # 
    # We store summary and headline in DB for performance and searchability reasons.
    # Heavy @-querying will be done at save time, not at display-time.
    # Both of them can contain links and minimal HTML formating.
    # Never let your users edit those fields directly, as they'll be flagged as html-safe!
    # If you want to change behaviour of those fields, override the preprocess_xxx methods.
    html_headline = models.CharField(max_length = 140)          # The computed headline (a-little-bit-more-than-a-title) for this content.
    html_summary = models.CharField(max_length = 1024)          # The computed summary for this content.
    text_headline = models.CharField(max_length = 140)          # The computed headline (a-little-bit-more-than-a-title) for this content.
    text_summary = models.CharField(max_length = 1024)          # The computed summary for this content.
    
    # Resources associated to this content
    resources = models.ManyToManyField(Resource, blank = True, null = True)
    
    # XXX TODO: Implement sources (ie. the client this 'tweet' is coming from)
    # source = "web"
    
    # List of field name / generation method name. This is very useful when translating content.
    # See twistrans.lib for more information
    # XXX TODO: Document and/or rename that?
    auto_values = (
        ("html_headline", "preprocess_html_headline", ),
        ("text_headline", "preprocess_text_headline", ),
        ("html_summary", "preprocess_html_summary", ),
        ("text_summary", "preprocess_text_summary", ),
    )
    # This points to the original version of a translated content.
    # (Not implemented yet, but will be one day.)
    translation_of = models.ForeignKey(
        "Content",
        related_name = "translated_versions",
        null = True,
        blank = True,
    )
    
    # Security models available for the user
    # XXX TODO: Use a foreign key instead with some clever checking, or, better create a new field type.
    permission_templates = permissions.content_templates
        
    # View overriding support.
    # This will be saved into the Content object for performance reasons.
    # That way you don't have to dereference the underlying object until you want to see the whole page.
    # Overload the 'type_summary_view' in your subclasses if you want.
    # Same for detail_view. Set to 'None' if no detail view (so no links on summary views)
    type_summary_view = "content/summary.part.html"
    type_detail_view = "content/view.html"
    
    is_content = True   # XXX TODO: What is this for, BTW??
    
    def __unicode__(self):
        return "%s %d by %s" % (self.model_name, self.id, self.owner)
    
    class Meta:
        app_label = 'twistranet'

    #                                                               #
    #                       Display management                      #
    # You can override this in your content types.                  #
    #                                                               #
    
    def preprocess_html_headline(self, text = None):
        """
        preprocess_html_headline => unicode string.
        
        Used to compute the headline displayed.
        You can have some logic to display a different headline according to the content's properties.
        Default is to display the first characters (or so) of the title, or of raw text content if title is empty.
        
        You can override this in your own content types if you want.
        """
        if text is None:
            text = getattr(self, "title", "")
        if not text:
            text = getattr(self, "text", "")
        MAX_HEADLINE_LENGTH = 140 - 5
        text = html.escape(text)
        if len(text) >= MAX_HEADLINE_LENGTH:
            text = u"%s [...]" % text[:MAX_HEADLINE_LENGTH]
        text = utils.escape_links(text)
        return text
        
    def preprocess_text_headline(self, text = None):
        """
        Default is just tag-stripping
        """
        if text is None:
            text = self.preprocess_html_headline()
        return html.strip_tags(text)
        
    def preprocess_html_summary(self, text = None):
        """
        Return an HTML-safe summary.
        Default is to keep the 1024-or-so first characters and to keep basic HTML formating.
        """
        if text is None:
            text = getattr(self, "description", "")
        if not text:
            text = getattr(self, "text", "")

        MAX_SUMMARY_LENGTH = 1024 - 10
        text = html.escape(text)
        if len(text) >= MAX_SUMMARY_LENGTH:
            text = u"%s [...]" % text[:MAX_SUMMARY_LENGTH]
        text = utils.escape_links(text)
        if text == self.preprocess_html_headline():
            text = ""

        return text
        
    def preprocess_text_summary(self, text = None):
        """
        Default is just tag-stripping
        """
        if text is None:
            text = self.preprocess_html_summary()
        return html.strip_tags(text)        
            
    # DO NOT OVERRIDE ANYTHING BELOW THIS LINE!

    #                                                               #
    #                   Content internal stuff                      #
    #                                                               #

    def save(self, *args, **kw):
        """
        Populate special content information before saving it.
        See Content class documentation for more information on that.
        """        
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

        # Check if user has modification rights for existing content
        if self.id:
            if not self.can_edit:
                raise PermissionDenied("You're not allowed to edit this content.")
                    
        # Set headline and summary cached values
        self.html_headline = self.preprocess_html_headline()
        self.text_headline = self.preprocess_text_headline()
        self.html_summary = self.preprocess_html_summary()
        self.text_summary = self.preprocess_text_summary()
        
        # Actually save stuff
        return super(Content, self).save(*args, **kw)
        

    def delete(self,):
        """
        Delete object after we've checked security
        """
        if self.id:
            if not self.can_delete:
                raise PermissionDenied("You're not allowed to delete this object.")
        return super(Content, self).delete()
