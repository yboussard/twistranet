"""
Special tags to escape various stuff in TN templates

"""
import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

register = template.Library()

# url_regex = re.compile( r"(?P<Protocol>(?:(?:ht|f)tp(?:s?)\:\/\/|~\/|\/)?)(?P<UsernamePassword>(?:\w+:\w+@)?)(?P<Subdomains>(?:(?:[-\w]+\.)+)(?P<TopLevelDomains>(?:com|org|net|gov|mil|biz|info|mobi|name|aero|jobs|museum|travel|[a-z]{2})))(?#Port)(?::[\d]{1,5})?(?#Directories)(?:(?:(?:\/(?:[-\w~!$+|.,=]|%[a-f\d]{2})+)+|\/)+|\?|#)?(?#Query)(?:(?:\?(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)(?:&(?:[-\w~!$+|.,*:]|%[a-f\d{2}])+=?(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)*)*(?#Anchor)(?:#(?:[-\w~!$+|.,*:=]|%[a-f\d]{2})*)?"
# )
# user_regex = re.compile(r"@(?P<Alias>[a-zA-Z_]\w*)")

@register.filter(name='escape_status')
@stringfilter
def escape_status(text, autoescape=None):
    """
    This safely escapes the HTML content and replace all links, @, etc by their TN counterpart.
    """
    raise NotImplemented("Moved into utils.escape_links.")
    # # Determine autoescape behaviour
    # if autoescape:
    #     text = conditional_escape(text)
    #     
    # # Replace xxx:// strings by <a href> tags
    # text = url_regex.sub('<a target="_blank" href="\g<0>">\g<Subdomains></a>', text)
    # 
    # # Replace @<alias> by the actual account link
    # s = text
    # for match in user_regex.finditer(text):
    #     s = "%s%s%s" % (
    #         s[0:match.start()],
    #         '<a href="%s">%s</a>' % (reverse('twistranet.views.account_by_name', args = (match.groupdict()['Alias'],)), match.group(0)),
    #         s[match.end():],
    #         )
    # text = s
    # 
    # return mark_safe(text)
    # 
    
escape_status.needs_autoescape = True

