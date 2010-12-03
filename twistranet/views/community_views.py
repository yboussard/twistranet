from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import *
from django.contrib import messages
from django.utils.translation import ugettext as _

from twistranet.forms import community_forms
from twistranet.lib.decorators import require_access

from twistranet.models import *
from base_view import BaseView
from account_views import AccountView
import settings


class CommunitiesView(BaseView):
    """
    A list of n first available (visible) communities
    """
    title = "Communities"
    
    def get_important_action(self):
        return None
    
    def __call__(self, request):
        self.request = request
        communities = Community.objects.get_query_set()[:settings.TWISTRANET_COMMUNITIES_PER_PAGE]
        return self.render_template(
            "community/list.html",
            {
                "communities":  communities,
            }
        )

class CommunityView(AccountView):
    """
    Individual Community View.
    By some aspects, this is very close to the account view.
    """
    important_action = None
    context_boxes = [
        'community/profile.box.html',
        'community/members.box.html',
    ]
    
    def __call__(self, request, value):
        self.request = request
        param = { self.lookup: value }
        self.community = get_object_or_404(Community, **param)
        return self.community_view(self.community)

    def get_title(self,):
        return _("%s community" % self.community.text_headline)

    def get_important_action(self):
        return self.important_action

    def community_view(self, community, ):
        """
        Account (user/profile) page.
        We just diplay posts of any given community.
        XXX TODO:
            - Check if community is listed and permit only if approved
        """
        # Generate forms and ensure proper redirection if applicable
        try:
            forms = self._getInlineForms(publisher = community)
        except MustRedirect:
            return HttpResponseRedirect(self.request.path)
            
        # If we can join, this is the important action
        if community.can_join:
            self.important_action = ("Join this community", reverse('twistranet_home'))

        # Generate the view itself
        return self.render_template(
            "community/view.html",
            {
                "path": self.request.path,
                "content_forms": forms,
                "community": community,
                "n_members": community.members.count(),
                "members": community.members_for_display[:settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS],
                "managers": community.managers_for_display[:settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS],
                "latest_content_list": self.get_recent_content_list(community),
            })



class CommunityEdit(CommunityView):
    """
    Edit form for community. Not so far from the view itself.
    """
    def community_edit(self, community):
        """
        Edition stuff
        """
        # Process form
        if request.method == 'POST': # If the form has been submitted...
            form = community_forms.CommunityForm(request.POST, instance = community)
            if form.is_valid(): # All validation rules pass
                community = form.save()
                return HttpResponseRedirect(community.get_absolute_url())
        else:
            form = community_forms.CommunityForm(instance = community) # An unbound form

        # Template hapiness
        return self.render_template(
            'community/edit.html',
            {
                "community": community,
                "n_members": community.members.count(),
                "members": community.members_for_display[:settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS],
                "form": form,
                "is_member": community and community.is_member,
            })
        return HttpResponse(t.render(c))


    def __call__(self, request, value):
        self.request = request
        param = { self.lookup: value }
        community = get_object_or_404(Community, **param)
        if not community.can_view:
            raise NotImplementedError("Should implement a permission denied exception here")
        if not community.can_edit:
            raise NotImplementedError("Should redirect to the regular view? or raise a permission denied exception here.")
        return self.community_edit(community)

class CommunityCreate(CommunityEdit):
    """
    Community creation. Close to the edit class
    """
    def __call__(self, request):
        return self.community_edit(None)


@require_access
def delete_community(request, community_id):
    """
    Delete a community by its id.
    The model checks the can_delete permission (of course).
    """
    community = Community.objects.get(id = community_id)
    name = community.name
    community.delete()
    messages.info(request, _('The community %(name)s has been deleted.' % {'name': name}))
    return HttpResponseRedirect(reverse('twistranet.views.home', ))



