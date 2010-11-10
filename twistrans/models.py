"""
The model for Twistrans.

Basically, we extend the ResourceManager and Resource functionnalities to handle field translations as resource objects.
"""
from twistranet.models import Resource, Content
from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist

class TranslationResource(Resource):
    """
    This is the actual translated stuff.
    """
    translation = models.TextField()
    original_field = models.CharField(max_length = 64, db_index = True)                                     # id. of the field in the original content
    original_content = models.ForeignKey("twistranet.Content", related_name = "_field_translations")        # Pointer to the very original content this is a translation of.

    def get(self,):
        """
        Shortcut to content
        """
        return self.content
        
    def save(self, *args, **kw):
        """
        """
        # Enforce some parameters
        if not self.language:
            raise ValidationError("A translated resource must have a language!")
        if not self.original_field:
            raise ValidationError("A translated resource must be associated to a content field")
        self.manager = None             # Translations are resources stored in the main database
        self.mimetype = "text/plain"
        self.encoding = "utf8"
        self.locator = "translation/%i/%s/%s" % (self.original_content.id, self.original_field, self.language, )
        try:
            self.owner
        except ObjectDoesNotExist:
            self.owner = self.original_content.author
        
        # Call parent's save method
        return super(TranslationResource, self).save(*args, **kw)


