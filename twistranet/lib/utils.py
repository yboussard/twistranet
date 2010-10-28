import re
import unicodedata

def slugify(value):
    """
    Transform a string value into a 50 characters slug
    """
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = unicode(re.sub(' +', '_', value))
    return value[:50]
    
    
def get_model_class(ob, base_class, type_value):
    """
    Return the actual subclass of 'ob'.
    Useful for Account and Content objects, to get the actual underlying type.
    Ex for a status update :
    c = Content.get(id = xxx)
    get_model_class(c, Content, c.content_type) === c.object
    
    XXX For some reason that doesn't work with account. __subclasses__ doesn't recognise GlobalCommunity to be a subclass of Account!
    """
    if not isinstance(ob, base_class):
        raise ValueError("ob must be an instance of base_class %s" % base_class.__name__)
    if not type_value:
        raise ValueError("You can't apply permissions before setting your %s" % ob.__class__.__name__)
    if type_value == ob.__class__.__name__:
        return ob.__class__
    for sub in base_class.__subclasses__():
        if sub.__name__ == type_value:
            return sub
    raise ValueError("Didn't find base class for %s/%s/%s" % (ob, base_class, type_value, ))
    
    