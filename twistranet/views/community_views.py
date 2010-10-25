from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import *

from twistranet.forms import communityforms

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
    current_account = account
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
            
            "i_am_in": community.members.filter(id = current_account.id).exists(),
        },
        )
    return HttpResponse(t.render(c))
    
def edit_community(request, community_id):
    """
    Edit the given community
    """
    # Get basic information
    account = request.user.get_profile()
    current_account = account
    community = Community.objects.get(id = community_id)
    if not community.can_view:
        raise NotImplementedError("Should implement a permission denied exception here")
    if not community.can_edit:
        raise NotImplementedError("Should redirect to the regular view? or raise a permission denied exception here.")

    # Process form
    if request.method == 'POST': # If the form has been submitted...
        form = communityforms.CommunityForm(request.POST, instance = community) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            form.save()
            return HttpResponseRedirect(reverse('twistranet.views.community_by_id', args = (community.id,)))
    else:
        form = communityforms.CommunityForm(instance = community) # An unbound form

    t = loader.get_template('community/edit.html')
    c = RequestContext(
        request,
        {
            "path": request.path,
            "account": account,
            "current_account": account,
            "community": community,
            "members": community.members.get_query_set()[:25],        # XXX SUBOPTIMAL
            "form": form,
            "i_am_in": community.members.filter(id = current_account.id).exists(),
        },
        )
    return HttpResponse(t.render(c))

    
    
def create_community(request):
    """
    """
    raise NotImplementedError("Still have to do this ;)")



