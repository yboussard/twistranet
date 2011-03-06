"""
Default content types for twistranet
"""
import mimetypes
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
    type_detail_link = False
    type_text_template_creation = "email/created_content_statusupdate.txt"
    type_html_template_creation = "email/created_content_statusupdate.html"
    _FORCE_SLUG_CREATION = False

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
    root_content = models.ForeignKey(Content, related_name = "comments", null = False, db_column = "_root_content_id")

    # Other type settings
    type_text_template_creation = "email/created_content_comment.txt"
    type_html_template_creation = "email/created_content_comment.html"
        
    def save(self, *args, **kw):
        """
        We ensure that in_reply_to and root_content are properly set.
        """
        # Compute the root_content value
        if not isinstance(self.in_reply_to, Content):
            raise ValueError("A comment must be in reply to a content")
        self.root_content = self.in_reply_to
        while isinstance(self.root_content, Comment):
            self.root_content = self.root_content.in_reply_to
            
        # Particularity here: we must be able to publish on the root_content to be allowed to comment.
        self.publisher = self.root_content.publisher

        # Ok; regular saving otherwise
        super(Comment, self).save(*args, **kw)
        
        # Additional notifications for comments (we don't care about checking if we're
        # in the creation mode, as comments should never be edited).
        listener_ids = [ l.id for l in self.listeners ]
        current = self.in_reply_to
        additional_listeners = []
        while current.id != self.root_content.id:
            for l in [ current.owner, ]:
                if not l.id in listener_ids and not l.id in additional_listeners:
                    additional_listeners.append(l)
        if additional_listeners:
            content_created.send(
                sender = self.__class__, 
                instance = self, 
                target = additional_listeners,
                text_template = self.model_class.type_text_template_creation,
                html_template = self.model_class.type_html_template_creation,
            )
    
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

    file = fields.ResourceField(allow_upload = True, allow_select = False, media_type='file')

    type_detail_view = "content/view.file.html"
    type_summary_view = "content/summary.file.html"
    default_picture_resource_slug = "default_resource_picture"

    @property
    def size(self):
        if self.file is not None:
            return formatbytes(self.file.resource_file.size)
            
    @property
    def is_image(self,):
        return self.file.is_image
        
    def save(self, *args, **kw):
        """
        Before saving, we use filename as this content title
        if title is empty, we set also picture.
        """
        if self.file is not None:
            self.picture = self.file

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



