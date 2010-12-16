"""
The magnifiscent TN searching stuff.
Uses haystack.
"""
from django.conf import settings
from haystack.views import SearchView
from django.http import HttpResponse, HttpResponseRedirect
from twistranet.core.lib.decorators import require_access
from base_view import BaseView, MustRedirect
from haystack.forms import ModelSearchForm
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage

RESULTS_PER_PAGE = getattr(settings, 'HAYSTACK_SEARCH_RESULTS_PER_PAGE', 20)

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



