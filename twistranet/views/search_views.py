"""
The magnifiscent TN searching stuff.
Uses haystack.
"""
from haystack.views import SearchView
from django.http import HttpResponse, HttpResponseRedirect
from twistranet.lib.decorators import require_access

class TwistraNetSearchView(SearchView):
    """
    We overload this to add critical search improvements:
    
    - pass 'account' in the context
    """
    
    def extra_context(self):
        """
        Append TN-specific stuff in the context
        """
        extra = super(TwistraNetSearchView, self).extra_context()

        # Add current account information
        extra['account'] = self.request.user.get_profile()

        # Add the facets
        if self.results == []:
            extra['facets'] = self.form.search().facet_counts()
        else:
            extra['facets'] = self.results.facet_counts()

        return extra


    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.
        Will redirect directly to the only 1 result if there is one.
        """
        # Many tests to check the unicity
        if self.results:
            if self.results.count() == 1:
                ret = self.results.all()[0]
                if ret.object.can_list:
                    # XXX TODO: Implement get_absolute_url() everywhere so that this method works!
                    url = getattr(ret.object, 'get_absolute_url', None)
                    if url:
                        return HttpResponseRedirect(url())

        return super(TwistraNetSearchView, self).create_response()

