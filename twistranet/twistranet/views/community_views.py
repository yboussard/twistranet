from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage
from django.shortcuts import *
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db.models import Q

from twistranet.twistranet.forms import community_forms
from twistranet.twistranet.lib.decorators import require_access

from twistranet.twistranet.models import *
from base_view import BaseView, MustRedirect, BaseObjectActionView
from account_views import UserAccountView, AccountListingView

from  twistranet.twistranet.lib.log import log

RESULTS_PER_PAGE = settings.HAYSTACK_SEARCH_RESULTS_PER_PAGE

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
        "n_managers",
        "is_member",
        "members",
        "managers", 
    ]
    model_lookup = Community
        
    def get_title(self,):
        return self.community.title
        
    def get_actions(self,):
        """
        Basic actions on communities
        """
        actions = []
        if not self.community:
            return []
        
        # Generate actions
        for act_view in (CommunityEdit, CommunityJoin, CommunityInvite, CommunityLeave, CommunityDelete, ):
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
        self.members = self.community and self.community.members_for_display[:settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS] or []
        self.managers = self.community and self.community.managers_for_display[:settings.TWISTRANET_DISPLAYED_COMMUNITY_MEMBERS] or []  
        self.n_managers = self.community and self.community.managers.count() or 0
        self.n_communities = []
        self.n_network_members = []




#                                                                               #
#                               LISTING VIEWS                                   #
#                                                                               #

class CommunityMembers(CommunityView):
    """
    list members for a community
    """
    template = "account/list.html"
    template_variables = CommunityView.template_variables + AccountListingView.template_variables

    def get_title(self,):
        return _("All members of %(name)s" % {'name': self.community.title} )

    def prepare_view(self, *args, **kw):
        super(CommunityMembers, self).prepare_view(*args, **kw)
        self.accounts = self.community.members


class CommunityManagers(CommunityMembers):
    """
    list managers for a community
    """

    def get_title(self,):
        return _("All managers of %(name)s" % {'name': self.community.title} )

    def prepare_view(self, *args, **kw):
        super(CommunityMembers, self).prepare_view(*args, **kw)
        self.accounts = self.community.managers    

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
        self.communities = Community.objects.get_query_set()[:settings.TWISTRANET_COMMUNITIES_PER_PAGE]

class MyCommunitiesView(BaseView):
    """
    A list of n communities I manage
    """
    title = "Communities I manage"
    template = "community/list.html"
    template_variables = BaseView.template_variables + [
        "communities",
    ]

    def prepare_view(self, ):
        super(CommunityListingView, self).prepare_view()
        auth = Account.objects._getAuthenticatedAccount()
        self.communities = Community.objects.filter(
            targeted_network__target__id = auth.id,
            requesting_network__client__id = auth.id,
            targeted_network__is_manager = True,
        )[:settings.TWISTRANET_COMMUNITIES_PER_PAGE]


    

#                                                                           #
#                           Edition / Action views                          #
#                                                                           #

class CommunityEdit(CommunityView):
    """
    Edit form for community. Not so far from the view itself.
    """
    template = "community/edit.html"
    content_forms = []
    latest_content_list = []
    
    action_label = "Edit"
    action_reverse_url = "community_edit"
    
    def get_form_class(self,):
        """
        You can use self.request and self.object to find your form here
        if you need to determinate it with an acute precision.
        """
        if isinstance(self.object, GlobalCommunity):
            form_class = community_forms.GlobalCommunityForm
        else:
            form_class = community_forms.CommunityForm
        
        return form_class
    
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
        return _("Edit %(name)s" % {'name' : self.object.title })


class CommunityCreate(CommunityEdit):
    """
    Community creation. Close to the edit class
    """
    context_boxes = []
    
    
class CommunityInvite(CommunityView):
    """
    Invite ppl in a community
    """
    # Various parameters
    model_lookup = Community
    title = "Invite people in this community"
    
    # Action rendering
    action_label = "Invite"
    action_confirm = None
    action_reverse_url = "community_invite"
    action_main = False
    
    context_boxes = [
        'community/profile.box.html', 
        'community/metadata.box.html',
        'actions/context.box.html',
        'community/members.box.html',
    ]
    template = "community/invite.html"
    template_variables = CommunityView.template_variables + [
        "q",
        "selectable",
    ]
    model_lookup = Community
    
    def prepare_view(self, value):
        """
        This either performs a search or invite ppl in this community
        """
        from haystack.query import SearchQuerySet
        
        super(CommunityInvite, self).prepare_view(value)
        self.q = self.request.GET.get("q", None)
        self.account_ids = []
        for k, v in self.request.POST.items():
            if k.startswith("account_id_"):
                self.account_ids.append(k[len("account_id_"):])
        
        # Perform the search. XXX Should use haystack one day...
        if self.q:
            # Search users
            # sqs = SearchQuerySet()
            # sqs = sqs.auto_query(self.q)
            # # sqs = sqs.filter_and(model_class = "UserAccount")
            # self.selectable = sqs.load_all()
            # self.selectable = sqs[:RESULTS_PER_PAGE]
            # self.selectable = [ s.object for s in self.selectable ]
            flt = UserAccount.objects.filter(
                Q(title__icontains = self.q) | Q(description__icontains = self.q) | Q(user__email__icontains = self.q)
            ).distinct()
        else:
            # Just display current user's network which is not yet part of the community
            flt = UserAccount.objects.filter(
                targeted_network__target__id = self.auth.id,
                requesting_network__client__id = self.auth.id,
            )
            flt = flt.exclude(
                targeted_network__target__id = self.community.id,
                requesting_network__client__id = self.community.id,
            )
        self.selectable = flt[:RESULTS_PER_PAGE]            
            
        # If we have some people to invite, just prepare invitations
        for id in self.account_ids:
            account = UserAccount.objects.get(id = int(id))
            self.community.invite(account)
            
        # Redirect to the community page with a nice message
        if self.account_ids:
            messages.info(self.request, _("Invitations has been sent."))
            raise MustRedirect(self.community.get_absolute_url())
                    
    def as_action(self, request_view):
        if not request_view.community.is_member:
            return None
        if not request_view.object.can_join:
            return None
        return super(CommunityInvite, self).as_action(request_view)
    
    
class CommunityJoin(BaseObjectActionView):
    model_lookup = Community
    action_label = "Join"
    action_confirm = "Do you want to join this community?"
    action_reverse_url = "community_join"
    action_main = True

    def as_action(self, request_view):
        if not request_view.object.can_join:
            return None
        if request_view.community.is_member:
            return None
        return super(CommunityJoin, self).as_action(request_view)
    
    def prepare_view(self, value):
        super(CommunityJoin, self).prepare_view(value)
        name = self.community.title
        if not self.community.can_join:
            # XXX Should send a message to community managers for approval
            raise NotImplementedError("We should implement approval here!")
        self.community.join()
        messages.info(self.request, _("You're now part of %(name)s!<br />Welcome aboard." % {'name': name}))
        raise MustRedirect(self.community.get_absolute_url())

class CommunityLeave(BaseObjectActionView):
    model_lookup = Community
    action_label = "Leave"
    action_confirm = "Do you really want to leave this community?"
    action_reverse_url = "community_leave"

    def as_action(self, request_view):
        if not request_view.community.is_member:
            return None
        if not request_view.object.can_leave:
            return None
        return super(CommunityLeave, self).as_action(request_view)

    def prepare_view(self, value, ):
        super(CommunityLeave, self).prepare_view(value)
        name = self.community.title
        if not self.community.can_leave:
            raise NotImplementedError("Should return permission denied!")
        self.community.leave()
        messages.info(self.request, _("You've left %(name)s." % {'name': name}))
        raise MustRedirect(self.community.get_absolute_url())


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
        name = self.community.title
        self.community.delete()
        messages.info(
            self.request, 
            _("'%(name)s' community has been deleted." % {'name': name})
        )
        raise MustRedirect(reverse("twistranet_home"))



