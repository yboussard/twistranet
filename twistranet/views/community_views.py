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
from base_view import BaseView, MustRedirect
from account_views import UserAccountView
from twistranet import twistranet_settings



class CommunityView(UserAccountView):
    """
    Individual Community View.
    By some aspects, this is very close to the account view.
    """
    context_boxes = [
        'community/profile.box.html',
        'actions/context.box.html',
        'community/members.box.html',
    ]
    template = "community/view.html"
    template_variables = UserAccountView.template_variables + [
        "community",
        "n_members",
        "is_member",
        "members",
        "managers", 
    ]
    model_lookup = Community
        
    def get_title(self,):
        return _("%(name)s community" % {'name': self.community.text_headline} )
        
    def get_actions(self,):
        """
        Basic actions on communities
        """
        actions = []
        if not self.community:
            return []
        
        # Contributor stuff
        if self.community.can_edit:
            actions.append({
                "label": _("Edit community"),
                "url": reverse("community_edit", args = (self.community.id, )),
            })

        # Join / Invite ppl
        if self.community.can_join:
            if not self.is_member:
                actions.append({
                    "label": _("Join this community"), 
                    "url": reverse('community_join', args = (self.community.id, )),
                    "main": True,
                    "confirm": _("Do you really want to join this community?"),
                })
            else:
                actions.append({
                    # If we have the "can_join" permission AND we're already a member, it means we may invite other people.
                    "label": _("Invite people"),
                    "url": reverse("twistranet_home"),
                    "main": False,
                })
        elif not self.is_member:
            actions.append({
                "label": _("Join this community"), 
                "url": reverse('community_join', args = (self.community.id, )),
                "main": True,
                "confirm": _("Do you really want to join this community? Your request will be send for approval to the community managers."),
            })
            
        # Leave this
        if self.community.can_leave:
            actions.append({
                "label": _("Leave this community"),
                "url": reverse("community_leave", args = (self.community.id, )),
                "confirm": _("Do you really want to leave this community?"),
            })
    
        return actions

    def prepare_view(self, *args, **kw):
        """
        Prepare community view
        """
        super(UserAccountView, self).prepare_view(*args, **kw)
        self.account = self.object
        self.n_members = self.community.members.count()
        self.is_member = self.community.is_member
        self.members = self.community.members_for_display[:twistranet_settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS]
        self.managers = self.community.managers_for_display[:twistranet_settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS]
        self.n_communities = []
        self.n_network_members = []




#                                                                               #
#                               LISTING VIEWS                                   #
#                                                                               #

class CommunityListingView(BaseView):
    """
    A list of n first available (visible) communities
    """
    title = "Communities"
    template = "community/list.html"
    template_variables = BaseView.template_variables + [
        "communities",
    ]

    def prepare_view(self, ):
        super(CommunityListingView, self).prepare_view()
        self.communities = Community.objects.get_query_set()[:twistranet_settings.TWISTRANET_COMMUNITIES_PER_PAGE]


class AccountCommunitiesView(UserAccountView):
    """
    All network members for an account.
    """
    template = CommunityListingView.template
    template_variables = UserAccountView.template_variables + CommunityListingView.template_variables

    def get_title(self,):
        if self.account.id == Account.objects._getAuthenticatedAccount().id:
            return _("My communities")
        return _("%(name)s's communities" % {'name': self.account.text_headline} )

    def prepare_view(self, *args, **kw):
        super(AccountCommunitiesView, self).prepare_view(*args, **kw)
        self.communities = self.account.communities



class CommunityEdit(CommunityView):
    """
    Edit form for community. Not so far from the view itself.
    """
    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if self.community:
            return _("Edit %(name)s" % {'name' : self.community.text_headline })
        return _("Create a community")

    def community_edit(self, community):
        """
        Edition stuff
        """
        self.community = community
        
        # Process form
        if self.request.method == 'POST': # If the form has been submitted...
            form = community_forms.CommunityForm(self.request.POST, instance = community)
            if form.is_valid(): # All validation rules pass
                community = form.save()
                return HttpResponseRedirect(community.get_absolute_url())
        else:
            form = community_forms.CommunityForm(instance = community) # An unbound form

        # Various data
        self.is_member = self.community and self.community.is_member

        # If the community already exists, we display its relevant information.
        dict_ = { 'form': form }
        if community:
            dict_.update({
                "community": community,
                "n_members": community.members.count(),
                "members": community.members_for_display[:twistranet_settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS],
                "is_member": community and community.is_member,
            })
        return self.render_template('community/edit.html', dict_)


    def view(self, value):
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
    context_boxes = [
    ]
    
    def view(self):
        return self.community_edit(None)

def join_community(request, community_id):
    """
    Join the given community
    """
    community = Community.objects.get(id = community_id)
    name = community.text_headline
    if not community.can_join:
        # XXX Should send a message to community managers for approval
        raise NotImplementedError("We should implement approval here!")
    community.join()
    messages.info(request, _("You're now part of %(name)s! Welcome aboard." % {'name': name}))
    return HttpResponseRedirect(community.get_absolute_url())



def leave_community(request, community_id):
    """
    Leave the given community
    """
    community = Community.objects.get(id = community_id)
    name = community.text_headline
    if not community.can_leave:
        # XXX Should send a pretty permission denied page
        raise NotImplementedError("You're not allowed to leave this")
    community.leave()
    messages.info(request, _("You've left %(name)s." % {'name': name}))
    return HttpResponseRedirect(reverse('twistranet_home'))

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



