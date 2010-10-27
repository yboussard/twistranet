from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import *
from django.contrib import messages
from django.utils.translation import ugettext as _


from twistranet.forms import communityforms

from twistranet.models import *
import account_views

def communities(request):
    """
    A list of n first available (visible) communities
    """
    account = request.user.get_profile()
    communities = Community.objects.get_query_set()
    t = loader.get_template('community/list.html')
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
    latest_list = Content.objects.filter(publisher = community).order_by("-created_at")

    # Form management
    try:
        forms = account_views._getInlineForms(request, community)
    except account_views.MustRedirect:
        return HttpResponseRedirect(request.path)

    # Generate template
    t = loader.get_template('community/view.html')
    c = RequestContext(
        request,
        {
            "path": request.path,
            "community": community,
            "members": community.members.get_query_set()[:25],        # XXX SUBOPTIMAL
            "latest_content_list": latest_list[:25],
            "community_forms": forms,
            
            "i_am_in": community.members.filter(id = account.id).exists(),
        },
        )
    return HttpResponse(t.render(c))
    

def community_by_name(request, community_name):
    """
    (not very very efficent)
    """
    account = request.user.get_profile()
    community = Community.objects.get(name = community_name)
    return community_by_id(request, community.id)

    
def edit_community(request, community_id = None):
    """
    Edit the given community
    """
    # Get basic information
    account = request.user.get_profile()
    if community_id is not None:
        community = Community.objects.get(id = community_id)
        if not community.can_view:
            raise NotImplementedError("Should implement a permission denied exception here")
        if not community.can_edit:
            raise NotImplementedError("Should redirect to the regular view? or raise a permission denied exception here.")
    else:
        # XXX TODO: Check some kind of "can_create_community" permission?
        community = None

    # Process form
    if request.method == 'POST': # If the form has been submitted...
        if community:
            form = communityforms.CommunityForm(request.POST, instance = community)
        else:
            form = communityforms.CommunityForm(request.POST)
            
        if form.is_valid(): # All validation rules pass
            community = form.save()
            return HttpResponseRedirect(reverse('twistranet.views.community_by_id', args = (community.id,)))
    else:
        if community:
            form = communityforms.CommunityForm(instance = community) # An unbound form
        else:
            form = communityforms.CommunityForm()

    # Template hapiness
    t = loader.get_template('community/edit.html')
    c = RequestContext(
        request,
        {
            "path": request.path,
            "account": account,
            "community": community,
            "members": community and community.members.get_query_set()[:25],        # XXX SUBOPTIMAL
            "form": form,
            "i_am_in": community and community.members.filter(id = account.id).exists(),
        },
        )
    return HttpResponse(t.render(c))

    
    
def create_community(request):
    """
    Simple, isn't it?
    """
    return edit_community(request, None)

def delete_community(request, community_id):
    """
    Delete a community by its id.
    The model checks the can_delete permission (of course).
    """
    account = request.user.get_profile()
    community = Community.objects.get(id = community_id)
    name = community.name
    community.delete()
    messages.info(request, _('The community %(name)s has been deleted.' % {'name': name}))
    return HttpResponseRedirect(reverse('twistranet.views.home', ))



