"""
Tags-specific views, including JSON stuff.
"""
import urllib
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import *
from django.contrib import messages
from django.utils.translation import ugettext as _

try:
    # python 2.6
    import json
except:
    # python 2.4 with simplejson
    import simplejson as json

from twistranet.twistapp.models import Content, Account
from twistranet.twistapp.forms import form_registry
from twistranet.twistapp.lib.log import *
from twistranet.core.views import *

class SearchTagsJSON(BaseView):
    """
    Search tags with a JSON output.
    """
    name = "tags_live_search"
    search_limit = 20       # Max nb of items to return
    
    def render_view(self, ):
        """
        Prepare JSON rendering.
        """
        from models import Tag
        
        # Inefficient search method
        search_string = self.request.GET['tag'].strip()
        if not search_string:
            q = Tag.objects.empty()
        else:
            q = Tag.objects.filter(title__icontains = search_string)
        
        # Format message
        q = q.order_by("title")[:self.search_limit].values("title", "id")
        msg = [ { "caption": flat['title'], "value": str(flat["id"]) } for flat in q ]
        
        # Return response
        return HttpResponse(
            json.dumps(msg),
            mimetype='text/html'
        )
