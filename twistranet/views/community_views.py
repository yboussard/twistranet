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
from base_view import BaseView, MustRedirect, BaseObjectActionView
from account_views import UserAccountView
from twistranet import twistranet_settings


class CommunityView(UserAccountView):
    """
    Individual Community View.
    By some aspects, this is very close to the account view.
    """
    context_boxes = [
        'community/profile.box.html', 
        'community/metadata.box.html',
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
        return self.community.text_headline
        
    def get_actions(self,):
        """
        Basic actions on communities
        """
        actions = []
        if not self.community:
            return []
        
        # Generate actions
        for act_view in (CommunityEdit, CommunityJoin, CommunityLeave, CommunityDelete, ):
            a = act_view(self.request).as_action(self)
            if a:
                actions.append(a)
    
        return actions

    def prepare_view(self, *args, **kw):
        """
        Prepare community view
        """
        super(UserAccountView, self).prepare_view(*args, **kw)
        self.account = self.object
        self.n_members = self.community and self.community.members.count() or 0
        self.is_member = self.community and self.community.is_member or False
        self.members = self.community and self.community.members_for_display[:twistranet_settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS] or []
        self.managers = self.community and self.community.managers_for_display[:twistranet_settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS] or []
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


    

#                                                                           #
#                           Edition / Action views                          #
#                                                                           #

class CommunityEdit(CommunityView):
    """
    Edit form for community. Not so far from the view itself.
    """
    template = "community/edit.html"
    form_class = community_forms.CommunityForm
    content_forms = []
    latest_content_list = []
    
    action_label = "Edit"
    action_reverse_url = "community_edit"
    
    def as_action(self, request_view):
        if not request_view.object.can_edit:
            return
        return super(CommunityView, self).as_action(request_view)
    
    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if not self.object:
            return _("Create a community")
        return _("Edit %(name)s" % {'name' : self.object.text_headline })


class CommunityCreate(CommunityEdit):
    """
    Community creation. Close to the edit class
    """
    context_boxes = []
    
    
class CommunityJoin(BaseObjectActionView):
    model_lookup = Community
    action_label = "Join"
    action_confirm = "Do you want to join this community?"
    action_reverse_url = "community_join"
    action_main = True

    def as_action(self, request_view):
        if not request_view.object.can_join:
            return None
        ret = super(CommunityJoin, self).as_action(request_view)
    
        # If we're talking about community member, then the action must reflect that
        if request_view.community.is_member:
            ret["label"] = _("Invite people")
            ret["url"] = reverse("twistranet_home")     # XXX TODO
            ret["main"] = False

        return ret
    
    def prepare_view(self, value):
        super(CommunityJoin, self).prepare_view(value)
        name = self.community.text_headline
        if not self.community.can_join:
            # XXX Should send a message to community managers for approval
            raise NotImplementedError("We should implement approval here!")
        self.community.join()
        messages.info(self.request, _("You're now part of %(name)s! Welcome aboard." % {'name': name}))
        self.redirect = self.community.get_absolute_url()

class CommunityLeave(BaseObjectActionView):
    model_lookup = Community
    action_label = "Leave"
    action_confirm = "Do you really want to leave this community?"
    action_reverse_url = "community_leave"

    def as_action(self, request_view):
        if not request_view.object.can_leave:
            return None
        return super(CommunityLeave, self).as_action(request_view)

    def prepare_view(self, value):
        super(CommunityLeave, self).prepare_view(value)
        name = self.community.text_headline
        if not self.community.can_leave:
            raise NotImplementedError("Should return permission denied!")
        self.community.leave()
        messages.info(self.request, _("You've left %(name)s." % {'name': name}))
        self.redirect = self.community.get_absolute_url()


class CommunityDelete(BaseObjectActionView):
    """
    Delete a community from the base
    """
    model_lookup = Community
    action_label = "Delete community"
    action_confirm = "Do you really want to delete this community?"
    action_reverse_url = "community_delete"
 
    def as_action(self, request_view):
        if not request_view.object.can_delete:
            return None
        return super(CommunityDelete, self).as_action(request_view)

    def prepare_view(self, *args, **kw):
        super(CommunityDelete, self).prepare_view(*args, **kw)
        self.redirect = reverse("twistranet_home")
        name = self.community.text_headline
        self.community.delete()
        messages.info(
            self.request, 
            _("'%(name)s' community has been deleted." % {'name': name})
        )
        self.redirect = reverse("twistranet_home")



