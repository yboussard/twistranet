import re
import unicodedata
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

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
    

url_regex = re.compile( r"(?P<Protocol>(?:(?:ht|f)tp(?:s?)\:\/\/|~\/|\/)?)(?P<UsernamePassword>(?:\w+:\w+@)?)(?P<Subdomains>(?:(?:[-\w]+\.)+)(?P<TopLevelDomains>(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2})))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:\/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|\/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"
)
user_regex = re.compile(r"@(?P<slug>[a-zA-Z_]\w*)")

def escape_links(text):
    """
    This safely escapes the HTML content and replace all links, @, etc by their TN counterpart.
    Use this to record the summary and/or headline of your content types.
    """
    # Security context
    from twistranet.models import Account
    auth = Account.objects._getAuthenticatedAccount()
    
    # Replace xxx:// strings by <a href> tags
    text = url_regex.sub('<a target="_blank" href="\g<0>">\g<Subdomains></a>', text)

    # Replace @<alias> by the actual account link
    match = user_regex.search(text) 
    while match is not None:
        try:
            account = Account.objects.distinct().get(slug = match.group(0)[1:])
        except ObjectDoesNotExist:
            # No account matching, we week things that way
            match =  user_regex.search(text, match.end())
            continue
        
        # Ok, serious stuff start now!
        replacement = '<a href="%s">%s</a>' % (reverse('twistranet.views.account_by_slug', args = (account.slug,)), account.text_headline)
        text = "%s%s%s" % (
            text[0:match.start()],
            replacement,
            text[match.end():],
            )
        # print text[match.start() + len(replacement):]
        match =  user_regex.search(text, match.start() + len(replacement))
        
    return text


