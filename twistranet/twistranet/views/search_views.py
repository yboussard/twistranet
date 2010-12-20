"""
The magnifiscent TN searching stuff.
Uses haystack.
"""
from django.conf import settings
from haystack.views import SearchView
from django.http import HttpResponse, HttpResponseRedirect
from twistranet.twistranet.lib.decorators import require_access
from base_view import BaseView, MustRedirect
from haystack.forms import ModelSearchForm
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage

try :
    #python 2.6
    import json
except :
    #python 2.4
    import simplejson as json

RESULTS_PER_PAGE = settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE
LIVE_SEARCH_RESULTS_NUMBER = 10
LIVE_SEARCH_THUMBS_SIZE = u'50x50'


class TwistraNetSearchView(BaseView):
    """
    We overload this and try to mix a little bit of the things we do with base_views...
    """
    template = 'search/search.html'
    template_variables = BaseView.template_variables + [
        "form",
        "page",
        "paginator",
        "query",
    ]
    title = "Search results"
    
    def basic_search(self, request, load_all=True, form_class=ModelSearchForm, searchqueryset=None, ):
        """
        Context::
            * form
              An instance of the ``form_class``. (default: ``ModelSearchForm``)
            * page
              The current page of search results.
            * paginator
              A paginator instance for the results.
            * query
              The query received by the form.
        """
        query = ''
        results = []

        if request.GET.get('q'):
            form = form_class(request.GET, searchqueryset=searchqueryset, load_all=load_all)

            if form.is_valid():
                query = form.cleaned_data['q']
                results = form.search()
        else:
            form = form_class(searchqueryset=searchqueryset, load_all=load_all)

        paginator = Paginator(results, RESULTS_PER_PAGE)

        try:
            page = paginator.page(int(request.GET.get('page', 1)))
        except InvalidPage:
            raise Http404("No such page of results!")

        self.form = form
        self.page = page
        self.paginator = paginator,
        self.query = query
        return results
            
    def prepare_view(self,):
        """
        Prepare response
        """
        super(TwistraNetSearchView, self).prepare_view()
        results = self.basic_search(self.request)
        
        # Many tests to check the unicity
        if results:
            if results.count() == 1:
                ret = results.all()[0]
                if ret.object.can_list:
                    url = getattr(ret.object, 'get_absolute_url', None)
                    if url:
                        raise MustRedirect(url())

class TwistraNetJSONSearchView(BaseView):
    """
    This view returns search results in json format
    used by live search
    """

    title = "Live Search results - return json data"

    def render_view(self, ):
        """
        must overload the standard
        twistranet render_view
        """
        data = self.basic_search(self.request)
        return HttpResponse( json.dumps(data),
                             mimetype='text/plain')


    
    def basic_search(self, request, load_all=True, form_class=ModelSearchForm, searchqueryset=None, ):
        """
        Context::
            * form
              An instance of the ``form_class``. (default: ``ModelSearchForm``)
            * query
              The query received by the form.
        """
        query = ''
        results = []

        if request.GET.get('q'):
            form = form_class(request.GET, searchqueryset=searchqueryset, load_all=load_all)

            if form.is_valid():
                query = form.cleaned_data['q']
                results = form.search()
        else:
            return []
        data = []
        for res in results[:LIVE_SEARCH_RESULTS_NUMBER] :
            o = {}
            if res.object is not None :
                res_obj = res.object
                o['title'] = getattr(res_obj, 'title', u'')
                o['type'] = type = getattr(res_obj, 'model_name', u'')
                o['description'] = getattr(res_obj, 'description', u'')  
                # for some kind of objects we get account or community url as url
                if type in ('StatusUpdate', ) :
                    owner = res_obj.owner_for_display()
                    o['title'] = owner.title
                    o['type'] = ''
                    o['link'] = owner.get_absolute_url() or '/'
                else :
                    o['link'] = res_obj.get_absolute_url() or '/'
                if hasattr(res_obj, 'picture') :
                    picture = res_obj.picture 
                else :
                    picture = res_obj.owner_for_display().picture
                if picture is not None :
                    from sorl.thumbnail import default
                    # generate the thumb or just get it
                    try :
                        thumb = default.backend.get_thumbnail( picture.image, LIVE_SEARCH_THUMBS_SIZE )
                        o['thumb'] = thumb.url 
                    except :
                        o['thumb'] = picture.get_absolute_url()
                else :
                    o['thumb'] = ''  
                data.append(o)
                
        return data
            
    def prepare_view(self,):
        """
        Prepare response
        """
        pass
                        

