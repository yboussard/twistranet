from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import html
import basemanager
from account import Account
from content import Content
from twistranet.lib import roles, permissions, languages

class StatusUpdate(Content):
    """
    StatusUpdate is the most simple content available (except maybe helloworld).
    It provides a good example of what you can do with a content type.
    """
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
    
    # View overriding support
    type_summary_view = "content/summary.notification.part.html"
    
    def __unicode__(self,):
        return u"Notification %d: %s" % (self.id, self.getText())
    
    def setText(self):
        """
        XXX TODO: Translate the sentence using gettext!
        """
        from django.core.urlresolvers import reverse
        if self.on_who:
            self.text = "@%s %s @%s" % (self.who.name, self.did_what, self.on_who.name)
        elif self.on_what:
            self.text = "@%s %s %s" % (self.who.name, self.did_what, self.on_what.id)
        else:
            self.text = "@%s" % (self.who, )
    
    class Meta:
        app_label = "twistranet"
        
        
class Document(Content):
    """
    A document is a (possibly long) text/html content associated with resource,
    with all the bells and whistle a CMS is expected to carry.
    
    Docs have a title so that's what is used (by now) as a headline.
    """
    
    class Meta:
        app_label = 'twistranet'

    title = models.CharField(max_length = 255)
    doc_summary = models.TextField()
    

    def setHTMLHeadline(self,):
        """
        Default is just tag-stripping without any HTML formating
        """
        self.html_headline = html.escape(self.title)


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
