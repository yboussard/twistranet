from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import html
from account import Account
from content import Content
from twistranet.lib import roles, permissions, languages

class StatusUpdate(Content):
    """
    StatusUpdate is the most simple content available (except maybe helloworld).
    It provides a good example of what you can do with a content type.
    """
    permission_templates = permissions.ephemeral_templates
    type_detail_view = None
    text = models.TextField()       # The basic text of the status update.

    class Meta:
        app_label = 'twistranet'

class Notification(Content):
    """
    ACCOUNT did WHAT [on ACCOUNT/CONTENT].
    This is an internal system message, available to people following either the first or second mentionned account.
    It's meant to be posted by SystemAccount only.
    
    Author is usually SystemAccount.
    Publisher is usually the community (or account) this content belongs to.
    """
    # Defined fields on the notification
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
    
    # View / permissions overriding support
    permission_templates = permissions.ephemeral_templates
    type_summary_view = "content/summary.notification.part.html"
    type_detail_view = None
    
    def __unicode__(self,):
        return u"Notification %d: %s" % (self.id, self.did_what)
    
    def preprocess_html_headline(self, text = None):
        """
        XXX TODO: Translate the sentence using gettext!
        """
        from django.core.urlresolvers import reverse
        if self.on_who:
            text = "@%s %s @%s" % (self.who.slug, self.did_what, self.on_who.slug)
        elif self.on_what:
            text = "@%s %s %s" % (self.who.slug, self.did_what, self.on_what.id)
        else:
            text = "@%s" % (self.who, )
        return super(Notification, self).preprocess_html_headline(text)
    
    class Meta:
        app_label = "twistranet"
        
        
class Document(Content):
    """
    A document is a (possibly long) text/html content associated with resource,
    with all the bells and whistle a CMS is expected to carry.
    """
    
    class Meta:
        app_label = 'twistranet'

    text = models.TextField()

    # def preprocess_html_headline(self,):
    #     """
    #     Default is just tag-stripping without any HTML formating
    #     """
    #     return html.escape(self.title)
    # 
    # def preprocess_html_summary(self,):
    #     """
    #     Same as regular summary but with our new field
    #     """
    #     return html.escape(self.description)


# class Link(Content):
#     class Meta:
#         app_label = 'twistranet'
#     
# class File(Content):
#     """
#     Abstract class which represents a File in database.
#     We just add filename information plus several methods to display it.
#     """
#     class Meta:
#         app_label = 'twistranet'
#     
# class Image(File):
#     """
#     Image file
#     """
#     class Meta:
#         app_label = 'twistranet'
#     
#     
# class Video(File):
#     """
#     Video content
#     """
#     class Meta:
#         app_label = 'twistranet'
# 
#     
# class Comment(Content):
#     """
#     Special comment handling. Comment is 'just' a special type of content.
#     Comments are not commentable themselves...
#     """
#     class Meta:
#         app_label = 'twistranet'
#     
