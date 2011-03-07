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
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.db.models import Q

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
from models import Tag

RESULTS_PER_PAGE = settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE

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


class TagView(BaseIndividualView):
    """
    Individual Content View.
    """
    context_boxes = [
        "tags/tag.box.html",
        "tags/experts.box.html",
    ]
    template = "tags/view.html"
    template_variables = BaseIndividualView.template_variables + [
        "tag",
        "page",
        "paginator",
    ]
    model_lookup = Tag
    name = "tag_by_id"

    def get_title(self,):
        return self.tag.title_or_description

    def get_tag_content(self):
        """
        Perform the appropriate query to get what is inside this tag.
        """
        return Content.objects.filter(
            Q(tags__id = self.tag.id) | \
            Q(publisher__tags__id = self.tag.id)
        ).distinct().order_by("-modified_at")

    def prepare_view(self, *args, **kw):
        """
        Prepare tag view.
        Basically, tag view is just a search of the most relevant content matching this tag.
        We also provide a paginator to browse results easily.
        """
        super(TagView, self).prepare_view(*args, **kw)
        paginator = Paginator(self.get_tag_content(), RESULTS_PER_PAGE)
        try:
            page = paginator.page(int(self.request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404("No such page of results!")
        self.page = page
        self.paginator = paginator  


