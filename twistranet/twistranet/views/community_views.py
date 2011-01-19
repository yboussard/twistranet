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
from django.utils.safestring import mark_safe
from django.db.models import Q

from twistranet.twistranet.forms import community_forms
from twistranet.twistranet.lib.decorators import require_access
from twistranet.actions import *

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
    title = None
        
    def get_title(self,):
        if not self.title:
            return self.community.title
        else:
            return super(CommunityView, self).get_title()
        
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

        # Check if there is content, display a pretty message if there's not
        if not len(self.latest_content_list):
            msg = _("""
        <p>There is not much content on this community. But it's up to YOU to create some!</p>
        <p>Feel free to add content with the simple form on this page.</p>
        <p>For example, you can express:<br />
        - What are you working on right now?<br />
        - What would you like to find on this community page?</p>""")
            messages.info(self.request, msg)


#                                                                               #
#                               LISTING VIEWS                                   #
#                                                                               #

class CommunityMembers(CommunityView):
    """
    list members for a community
    """
    template = "account/list.html"
    template_variables = CommunityView.template_variables + AccountListingView.template_variables
    name = "community_members"

    def get_title(self,):
        return _("All members of %(name)s") % {'name': self.community.title}

    def prepare_view(self, *args, **kw):
        super(CommunityMembers, self).prepare_view(*args, **kw)
        self.accounts = self.community.members

class CommunityManagers(CommunityMembers):
    """
    list managers for a community
    """
    name = "community_managers"

    def get_title(self,):
        return _("All managers of %(name)s") % {'name': self.community.title}

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
    name = "communities"

    def prepare_view(self, ):
        super(CommunityListingView, self).prepare_view()
        self.communities = Community.objects.get_query_set()[:settings.TWISTRANET_COMMUNITIES_PER_PAGE]

class CommunityInvitations(CommunityListingView, UserAccountView):
    """
    Pending invitations to communities
    """
    template = CommunityListingView.template
    template_variables = UserAccountView.template_variables + CommunityListingView.template_variables
    title = "Community invitations"
    name = "community_invitations"
    category = ACCOUNT_ACTIONS
    
    def as_action(self,):
        """Only return the action if there's pending nwk requests
        """
        auth = UserAccount.objects._getAuthenticatedAccount()
        req = auth.get_pending_network_requests(returned_model = Community)
        if not req:
            return
        action = BaseView.as_action(self)
        action.label = mark_safe(_('<span class="badge">%(number)d</span> Community invitations') % {"number": len(req)})
        return action
            
    def prepare_view(self, *args, **kw):
        auth = Account.objects._getAuthenticatedAccount()
        super(CommunityInvitations, self).prepare_view()
        UserAccountView.prepare_view(self, auth.id)
        self.communities = self.account.get_pending_network_requests(returned_model = Community)
    

class MyCommunitiesView(BaseView):
    """
    A list of n communities I manage
    """
    title = "Communities I manage"
    template = "community/list.html"
    template_variables = BaseView.template_variables + [
        "communities",
    ]
    name = "my_communities"
    category = ACCOUNT_ACTIONS
    
    def as_action(self,):
        auth = Account.objects._getAuthenticatedAccount()
        if not Account.objects.filter(
            targeted_network__target__id = auth.id,
            requesting_network__client__id = auth.id,
            requesting_network__is_manager = True,
            ).exists():
            return None
        return super(MyCommunitiesView, self).as_action()

    def prepare_view(self, ):
        super(MyCommunitiesView, self).prepare_view()
        auth = Account.objects._getAuthenticatedAccount()
        self.communities = Community.objects.filter(
            targeted_network__target__id = auth.id,
            requesting_network__client__id = auth.id,
            requesting_network__is_manager = True,
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
    name = "community_edit"
    category = LOCAL_ACTIONS
    title = None
    form_class = community_forms.CommunityForm
    
    def as_action(self, ):
        if not isinstance(getattr(self, "object", None), self.model_lookup):
            return None
        if not self.object.can_edit:
            return
        return super(CommunityView, self).as_action()
    
    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if self.title:
            return super(CommunityEdit, self).get_title()
        if not self.object:
            return _("Create a community")
        return _("Edit community")
        
        
class ConfigurationEdit(CommunityEdit):
    name = "twistranet_config"
    form_class = community_forms.AdministrationForm
    title = "Configuration"
    category = GLOBAL_ACTIONS
    
    def as_action(self,):
        """
        Check that I'm an admin
        """
        glob = GlobalCommunity.get()
        if not glob.can_edit:
            return None
        return BaseView.as_action(self,)
        
    def prepare_view(self):
        glob_id = GlobalCommunity.get().id
        super(ConfigurationEdit, self).prepare_view(glob_id)


class CommunityCreate(CommunityEdit):
    """
    Community creation. Close to the edit class
    """
    context_boxes = []
    category = ACCOUNT_ACTIONS
    title = "Create a community"
    name = "community_create"
    
    def as_action(self):
        if not Community.objects.can_create:
            return None
        return BaseView.as_action(self)
    
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
            
        # XXX SUBOPTIMAL PART
        self.selectable = flt[:RESULTS_PER_PAGE]
        member_ids = self.community.members.values_list('id', flat = True)
        self.selectable = [ u for u in self.selectable if u.id not in member_ids ]
            
        # If we have some people to invite, just prepare invitations
        for id in self.account_ids:
            account = UserAccount.objects.get(id = int(id))
            self.community.invite(account)
            
        # Redirect to the community page with a nice message
        if self.account_ids:
            messages.info(self.request, _("Invitations has been sent."))
            raise MustRedirect(self.community.get_absolute_url())
                    
    def as_action(self):
        if not isinstance(getattr(self, "object", None), self.model_lookup):
            return None
        if not self.object.is_member:
            return None
        if not self.object.can_join:
            return None
        return super(CommunityInvite, self).as_action()
    
    
class CommunityJoin(BaseObjectActionView):
    model_lookup = Community
    name = "community_join"
    category = MAIN_ACTION
    title = "Join community"
    confirm = "Do you really want to join this community?"

    def as_action(self):
        if not isinstance(getattr(self, "object", None), self.model_lookup):
            return None
        if not self.object.can_join:
            # XXX TODO: Implement request join!
            return None
        if self.object.is_member:
            return None
        return super(CommunityJoin, self).as_action()
    
    def prepare_view(self, value):
        super(CommunityJoin, self).prepare_view(value)
        name = self.community.title
        if not self.community.can_join:
            # XXX Should send a message to community managers for approval
            raise NotImplementedError("We should implement approval here!")
        self.community.join()
        messages.info(self.request, _("You're now part of %(name)s!<br />Welcome aboard.") % {'name': name})
        raise MustRedirect(self.community.get_absolute_url())

class CommunityLeave(BaseObjectActionView):
    model_lookup = Community
    category = LOCAL_ACTIONS
    name = "community_leave"
    title = "Leave community"
    confirm = "Do you really want to leave this community?"

    def as_action(self):
        if not isinstance(getattr(self, "object", None), self.model_lookup):
            return None
        if not self.object.is_member:
            return None
        if not self.object.can_leave:
            return None
        return super(CommunityLeave, self).as_action()

    def prepare_view(self, value, ):
        super(CommunityLeave, self).prepare_view(value)
        name = self.community.title
        if not self.community.can_leave:
            raise NotImplementedError("Should return permission denied!")
        self.community.leave()
        messages.info(self.request, _("You've left %(name)s.") % {'name': name})
        raise MustRedirect(self.community.get_absolute_url())


class CommunityDelete(BaseObjectActionView):
    """
    Delete a community from the base
    """
    model_lookup = Community
    name = "community_delete"
    confirm = _("Do you really want to delete this community?")
    title = "Delete community"
 
    def as_action(self):
        if not isinstance(getattr(self, "object", None), self.model_lookup):
            return None
        if not self.object.can_delete:
            return None
        return super(CommunityDelete, self).as_action()

    def prepare_view(self, *args, **kw):
        super(CommunityDelete, self).prepare_view(*args, **kw)
        name = self.community.title
        self.community.delete()
        messages.info(
            self.request, 
            _("'%(name)s' community has been deleted.") % {'name': name},
        )
        raise MustRedirect(reverse("twistranet_home"))



