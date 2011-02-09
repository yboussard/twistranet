"""
Default content types for twistranet
"""
from django.db import models
from twistranet.twistapp.lib import permissions   
from twistranet.twistapp.lib.utils import formatbytes
from twistranet.twistapp.models.content import Content
from twistranet.twistapp.models import fields

class StatusUpdate(Content):
    """
    StatusUpdate is the most simple content available (except maybe helloworld).
    It provides a good example of what you can do with a content type.
    """
    permission_templates = permissions.ephemeral_templates
    type_detail_view = None

    class Meta:
        app_label = 'twistapp'
        
class Comment(StatusUpdate):
    """
    A comment looks similar to StatusUpdate, but with the addition of a parent attribute,
    specifying which content this is a reply to.
    """
    # The Content or Comment this is a reply to
    in_reply_to = models.ForeignKey(Content, related_name = "direct_comments", null = False)
    # The original content this is a (possibly indirect) reply to
    _root_content = models.ForeignKey(Content, related_name = "comments", null = False)
    
    def save(self, *args, **kw):
        """
        We ensure that in_reply_to and _root_content are properly set.
        """
        # Compute the _root_content value
        if not isinstance(self.in_reply_to, Content):
            raise ValueError("A comment must be in reply to a content")
        self._root_content = self.in_reply_to
        while isinstance(self._root_content, Comment):
            self._root_content = self._root_content.in_reply_to
            
        # Particularity here: we must be able to publish on the _root_content to be allowed to comment.
        self.publisher = self._root_content.publisher

        # Ok; regular saving otherwise
        super(Comment, self).save(*args, **kw)
    
    class Meta:
        app_label = 'twistapp'

class Document(Content):
    """
    A document is a (possibly long) text/html content associated with resource,
    with all the bells and whistle a CMS is expected to carry.
    """
    class Meta:
        app_label = 'twistapp'

    text = models.TextField()

class File(Content):
    """
    Abstract class which represents a File (as a Resource) in database.
    We just add filename information plus several methods to display it.

    A file can always be uploaded (or re-uploaded or kept in place) but can never
    be selected amongst current resources.
    """
    class Meta:
        app_label = 'twistapp'

    file = fields.ResourceField(allow_select = False)

    type_detail_view = "content/view.file.html"
    type_summary_view = "content/summary.file.html"

    @property
    def size(self) :
        file = self.file.resource_file
        if self.file is not None :
            return formatbytes(self.file.resource_file.size)
        
    def save(self, *args, **kw):
        """
        Before saving, we use filename as this content title
        if title is empty.
        """
        if not self.title:
            self.title = self.file.title

        return super(File, self).save(*args, **kw)

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



