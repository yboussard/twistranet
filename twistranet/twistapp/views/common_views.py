from django.http import Http404, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.http import http_date
from twistranet.twistapp.lib.decorators import require_access


def js_vars(request):
    """
    return javascript dynamic stuff
    like home_url, possible translations
    or any contextual variables
    that can be used in javascript
    """
    src = """
var home_url = '%(home_url)s';
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