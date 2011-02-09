from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.utils.http import http_date
from twistranet.twistapp.lib.decorators import require_access
from twistranet.twistapp.views.account_views import PublicTimelineView
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.conf import settings

def js_vars(request):
    """
    return javascript dynamic stuff
    like home_url, possible translations
    or any contextual variables
    that can be used in javascript
    """
    src = """
var home_url = '%(home_url)s';
var jq = jQuery;
    """

    js_vars = dict(
        home_url = reverse("twistranet_home"),
    )

    response = HttpResponse( src %js_vars,
                             mimetype='text/javascript', )
    response['Cache-Control'] = 'public,max-age=604800'
    response['Last-Modified'] = http_date()
    response['Content-Type'] = 'application/x-javascript;charset=utf-8'

    return response


#                                                                                   #
#                                   Error pages                                     #
#                                                                                   #


class ErrorBaseView(PublicTimelineView):
    name = "error"
    title = _("Error")
    error_description = _("<p>Error on page <strong>%(requested_url)s</strong></p>")

    def prepare_view(self, *args, **kw):
        """
        Add a few parameters for the view
        """                     
        super(ErrorBaseView, self).prepare_view(*args, **kw)
        meta_infos = self.request.META
        requested_url = '%s//%s%s' %(meta_infos.get('wsgi.url_scheme',''),
                                     meta_infos.get('HTTP_HOST',''),
                                     meta_infos.get('PATH_INFO',''),)
        messages.warning(self.request, self.error_description %{'requested_url' : requested_url})


    
class Error404View(ErrorBaseView):
    name = "error404"
    title = _("Sorry, page not found")
    response_handler_method = HttpResponseNotFound
    error_description = _("""<p>
  The page <em>%(requested_url)s</em> doesn't exist on this site!
</p>
<p>
  Please contact the site administrator.
</p>
<p>
  Sorry for the inconvenience.
</p>""")


class Error500View(ErrorBaseView):
    name = "error500"
    title = _("Internal error")
    response_handler_method = HttpResponseServerError
    error_description = _("""<p>
  The page <span style="color:#E00023">%(requested_url)s</span> raises an error!
</p>
<p>
  Please contact the site administrator.
</p>
<p>
  Sorry for the inconvenience.
</p>""")
