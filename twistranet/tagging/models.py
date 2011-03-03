"""
Models for the 'tag' object used by twistranet.
"""
from django.db import models
from twistranet.twistapp.models import Twistable
from twistranet.twistapp.lib import permissions   
from twistranet.twistapp.models import fields

class Tag(Twistable):
    """
    The Tag content is used to categorize content quite freely.
    We inherit from Twistable so that we can benefit from most of the twistable features,
    BUT you have to know that a Tag object is **NOT** secured and should be considered
    as always visible!
    """
    # Tag attributes.
    # Most of them (title, descr, ...) are derived from twistable, but a Tag can be bound
    # to as many Twistables as we want, plus tags can be nested (hence the 'parent' attribute).
    parent = models.ForeignKey("self", related_name = "children", null = True, blank = True)
    
    # Disable security model for tags (it's not necessary to have it, in fact)
    objects = models.Manager()
    _ALLOW_NO_PUBLISHER = True
    permission_templates = permissions.public_template
    
    # Behaviour overload
    def getDefaultPublisher(self,):
        """
        Default publisher is always None for tags.
        But we can imagine in further versions to have tag DOMAINS.
        """
        return None

    class Meta:
        app_label = 'twistapp'
