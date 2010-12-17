from django.db import models
from twistranet.twistranet.lib import permissions
from content import Content

class StatusUpdate(Content):
    """
    StatusUpdate is the most simple content available (except maybe helloworld).
    It provides a good example of what you can do with a content type.
    """
    permission_templates = permissions.ephemeral_templates
    type_detail_view = None
    # text = models.TextField()       # The basic text of the status update.

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
