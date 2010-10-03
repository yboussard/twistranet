from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


from twistranet.models import *
import account_views

def communities(request):
    """
    A list of n first available (visible) communities
    """
    account = request.user.get_profile()
    communities = Community.objects.get_query_set()
    t = loader.get_template('communities.html')
    c = RequestContext(
        request,
        {
            "path":         request.path,
            "account":      account,
            "communities":  communities[:25],
        })
    return HttpResponse(t.render(c))

def community_by_id(request, community_id):
    """
    Display a pretty community page.
    Here you can view all members and posts published on this community
    """
    account = request.user.get_profile()
    community = Community.objects.get(id = community_id)
    latest_list = Content.objects.filter(publisher = community).order_by("-date")

    # Form management
    try:
        forms = account_views._getInlineForms(request, community)
    except account_views.MustRedirect:
        return HttpResponseRedirect(request.path)

    # Generate template
    t = loader.get_template('community.html')
    c = RequestContext(
        request,
        {
            "path": request.path,
            "account": account,
            "community": community,
            "members": community.members.get_query_set()[:25],        # XXX SUBOPTIMAL
            "latest_content_list": latest_list[:25],
            "community_forms": forms,
        },
        )
    return HttpResponse(t.render(c))
    


