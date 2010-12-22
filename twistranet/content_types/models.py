
"""
Default content types for twistranet
"""
from django.db import models
from twistranet.twistranet.lib import permissions
from twistranet.twistranet.models.content import Content
from twistranet.twistranet.forms import fields


class StatusUpdate(Content):
    """
    StatusUpdate is the most simple content available (except maybe helloworld).
    It provides a good example of what you can do with a content type.
    """
    permission_templates = permissions.ephemeral_templates
    type_detail_view = None

    class Meta:
        app_label = 'twistranet'



class Document(Content):
    """
    A document is a (possibly long) text/html content associated with resource,
    with all the bells and whistle a CMS is expected to carry.
    """

    class Meta:
        app_label = 'twistranet'

    text = models.TextField()


# class Link(Content):
#     class Meta:
#         app_label = 'twistranet'
#

class File(Content):
    """
    Abstract class which represents a File (as a Resource) in database.
    We just add filename information plus several methods to display it.

    A file can always be uploaded (or re-uploaded or kept in place) but can never
    be selected amongst current resources.
    """
    class Meta:
        app_label = 'twistranet'

    file = fields.ResourceField(allow_select = False)

    type_detail_view = "content/view.file.html"
    type_summary_view = "content/summary.file.html"

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



