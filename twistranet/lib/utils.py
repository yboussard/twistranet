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
    
    
    