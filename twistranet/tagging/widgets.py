import os
import traceback
import mimetypes
from django import forms
from django.db import models
from django.conf import settings
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from sorl.thumbnail import default
from django.template import loader, Context
from django.core.urlresolvers import reverse

from twistranet.twistapp.lib.log import log

try:
    # python 2.6
    import json
except:
    # python 2.4 with simplejson
    import simplejson as json

N_DISPLAYED_ITEMS = 30         # Number of images to display in the inline field


class TagsWidget(forms.SelectMultiple):
    def _media(self):
        base_url = settings.MEDIA_URL
        while base_url.endswith('/'):
            base_url = base_url[:-1]
        return forms.Media(
            css = {
                'all': ('%s/static/js/FCBKcomplete/style.css' % base_url, ),
            },
            js = ('%s/static/js/FCBKcomplete/jquery.fcbkcomplete.min.js' % base_url, )
        )
    media = property(_media)

    def render(self, name, value, attrs=None):
        """
        Returns this Widget rendered as HTML, as a Unicode string.
        
        This renders the basic input field, it's a no-brainer now.
        """
        from models import Tag
        
        rendered = super(TagsWidget, self).render(name, value, attrs)
        final_attrs = self.build_attrs(attrs, name = name)
        final_attrs['json_url'] = reverse('tags_live_search')
        rendered += """
        <script type="text/javascript">
            jq(document).ready(function(){                
                jq("#%(id)s").fcbkcomplete({
                    json_url: "%(json_url)s",
                    cache:          false,
                    filter_case:    false,
                    newel:          true
                });
            });
        </script>""" % final_attrs
        return mark_safe(rendered)
        
        
    def value_from_datadict(self, data, files, name):
        """
        Return data from the name[] field (with brackets added by FCBKcomplete)
        """
        data.setlist(name, data.getlist("%s[]" % name))
        return super(TagsWidget, self).value_from_datadict(data, files, name)

