import re
import unicodedata
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

# List of words you're not allowed to use as a slug
RESERVED_KEYWORDS = [
    "new",
    "id",
    "join",
    "create",
    "delete",
]

rsvd_kw = "$|".join(RESERVED_KEYWORDS)
SLUG_REGEX = r"(?!%s$)[a-zA-Z_][a-zA-Z0-9_\-\.]+" % rsvd_kw

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
    
