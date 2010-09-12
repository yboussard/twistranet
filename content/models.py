from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Content(models.Model):
    """
    Abstract content representation class.
    """
    text = models.TextField()
    date = models.DateTimeField()
    content_type = models.TextField()
    author = models.ForeignKey(User)

    def getText(self):
        """
        Override this to not use the 'text' attribute of the super class
        """
        return self.text

    
class StatusUpdate(Content):
    pass
    
    
class Link(Content):
    pass
    
    
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
