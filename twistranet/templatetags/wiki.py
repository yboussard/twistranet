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
from twistranet.lib import slugify
from twistranet.models import Account, Content

register = template.Library()

url_regex = re.compile( r"(?P<Protocol>(?:(?:ht|f)tp(?:s?)\:\/\/|~\/|\/)?)(?P<UsernamePassword>(?:\w+:\w+@)?)(?P<Subdomains>(?:(?:[-\w]+\.)+)(?P<TopLevelDomains>(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2})))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:\/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|\/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"
)
account_slug_regex = re.compile(r"@(?P<Alias>%s)" % slugify.SLUG_REGEX)
account_id_regex = re.compile(r"@(?P<Alias>\d+)")
content_slug_regex = re.compile(r"\[\s*(?P<Alias>%s)\s*\]" % slugify.SLUG_REGEX)
content_id_regex = re.compile(r"\[\s*(?P<Alias>\d+)\s*\]")

matches = (
    # regex,                fast_reverse,               model,          lookup field
    (account_id_regex,      'account_by_id',            Account,        "id",               ),
    (account_slug_regex,    'account_by_slug',          Account,        "slug",             ),
    (content_id_regex,      'content_by_id',            Content,        "id",               ),
    (content_slug_regex,    'content_by_slug',          Content,        "slug",             ),
)


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
    for regex, fast_reverse, model_class, lookup_field in matches:
        s = text
        for match in regex.finditer(text):
            label = match.group(0)
            title = None
            if lookup:
                try:
                    kw = {lookup_field: match.groupdict()['Alias']}
                    obj = model_class.objects.get(**kw)
                    url = obj.get_absolute_url()
                    if lookup_field != "slug" and obj.slug:
                        label = match.group(0).replace(match.groupdict()['Alias'], obj.slug)
                    title = obj.title
                except model_class.DoesNotExist:
                    continue    # Ignore unexistant or not-available links
            else:
                url = reverse(fast_reverse, args = (match.groupdict()['Alias'],))
            s = "%s%s%s" % (
                s[0:match.start()],
                '<a href="%s" title="%s">%s</a>' % (url, title or label, label),
                s[match.end():],
                )
        text = s
    
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
