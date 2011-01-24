"""
Extensible and extended wiki syntax management.

Basically, any 'wikied' page can contain, at your choice:
- @slug to point to the given username
- email@test.com to mailto:email@test.com
- http://www.google.com/xxx to <a href="blabla">www.google.com</a>
- [slug] or [id] to <a href="/content/slug"> or <a href="/content/id">
"""
import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django_twistranet.twistranet.lib import slugify
from django_twistranet.twistranet.models import Account, Content, Resource

from  django_twistranet.twistranet.lib.log import log

register = template.Library()

url_regex = re.compile( r"(?P<Protocol>(?:(?:ht|f)tp(?:s?)\:\/\/|~\/|\/)?)(?P<UsernamePassword>(?:\w+:\w+@)?)(?P<Subdomains>(?:(?:[-\w]+\.)+)(?P<TopLevelDomains>(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2})))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:\/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|\/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"
)
account_slug_regex = re.compile(r"@(?P<Alias>%s)" % slugify.SLUG_REGEX)
account_id_regex = re.compile(r"@(?P<Alias>\d+)")
content_slug_regex = re.compile(r"\[\s*(?P<Alias>%s)\s*\]" % slugify.SLUG_REGEX)
content_id_regex = re.compile(r"\[\s*(?P<Alias>\d+)\s*\]")

def resource_image(resource):
    """
    Render a resource image as an HTML tag
    """
    d = {
        'url':  resource.get_absolute_url(),
        'title': resource.title or "",
    }
    return """<img src="%(url)s" alt="%(title)s" />""" % d


matches = (
    # regex,                fast_reverse,         func,       model,          lookup field
    (account_id_regex,      'account_by_id',      None,       Account,        "id",               ),
    (account_slug_regex,    'account_by_slug',    None,       Account,        "slug",             ),
    (content_id_regex,      'content_by_id',      None,       Content,        "id",               ),
    (content_slug_regex,    'content_by_slug',    None,       Content,        "slug",             ),
    (content_id_regex,      'resource_by_id',     resource_image,             Resource,       "id",               ),
    (content_slug_regex,    'resource_by_slug',   resource_image,             Resource,       "slug",             ),
)


class Subf(object):
    def __init__(self, lookup, fast_reverse, func, model, lookup_field, ):
        self.lookup = lookup
        self.fast_reverse = fast_reverse
        self.func = func
        self.model = model
        self.lookup_field = lookup_field


    def __call__(self, match):
        """
        Function passed to re.sub()
        """
        label = match.group(0)
        title = None
        if self.lookup:
            try:
                kw = {self.lookup_field: match.groupdict()['Alias']}
                obj = self.model.objects.get(**kw)
                url = obj.get_absolute_url()
                if self.lookup_field != "slug" and obj.slug:
                    label = match.group(0).replace(match.groupdict()['Alias'], obj.slug)
                title = obj.title
            except self.model.DoesNotExist:
                log.debug("Doesn't exist: %s->%s" % (self.lookup_field, match.groupdict()['Alias']))
                return match.group(0)
        else:
            url = reverse(self.fast_reverse, args = (match.groupdict()['Alias'],))

        if self.func and obj:
            subst = self.func(obj)
        else:
            subst = '<a href="%s" title="%s">%s</a>' % (url, title or label, label)

        return subst


def escape_wiki(text, lookup = False, autoescape=None):
    """
    This safely escapes the HTML content and replace all links, @, etc by their TN counterpart.
    We've got two versions:
    - the fast one which doesn't lookup actual values
    - the slow one which may wake every single object mentionned in the text.
    Use whichever suits you the most.
    """
    
    # Determine autoescape behaviour
    if autoescape:
        text = conditional_escape(text)
        
    # Replace xxx:// strings by <a href> tags
    text = url_regex.sub('<a target="_blank" href="\g<0>">\g<Subdomains></a>', text)
    
    # Replace the global matches
    for regex, fast_reverse, func, model_class, lookup_field in matches:
        subf = Subf(lookup, fast_reverse, func, model_class, lookup_field )
        text = regex.sub(subf, text)
    
    # Return text
    return mark_safe(text)
    


@register.filter(name='wiki')
@stringfilter
def fast_wiki(text, autoescape=None):
    """
    This safely escapes the HTML content and replace all links, @, etc by their TN counterpart.
    """
    return escape_wiki(text, False, autoescape)

@register.filter(name='fullwiki')
@stringfilter
def slow_wiki(text, autoescape=None):
    """
    This safely escapes the HTML content and replace all links, @, etc by their TN counterpart.
    """
    return escape_wiki(text, True, autoescape)
    
    
slow_wiki.needs_autoescape = True
fast_wiki.needs_autoescape = True
