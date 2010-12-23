# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.conf import settings

from twistranet.twistranet.models import *
from twistranet.twistranet.forms import account_forms
from base_view import *

class UserAccountView(BaseWallView):
    """
    This is what is used as a base view for accounts
    """
    context_boxes = [
        'account/profile.box.html',
        'actions/context.box.html',
        'account/relations.box.html',
    ]
    
    template_variables = BaseWallView.template_variables + [
        "account",
        "n_communities",
        "n_network_members",
        "is_home",
    ]
    
    is_home = False
    model_lookup = UserAccount
    template = "account/view.html"
    
    def get_actions(self,):
        """
        Actions available on account (or home) pages
        """
        actions = []
        if self.account :
            self.auth_account = Account.objects._getAuthenticatedAccount()
            self.in_my_network = self.auth_account.network.filter(id = self.account.id)
            actions = [ self.get_action_from_view(view) for view in (AddToNetworkView, RemoveFromNetworkView, UserAccountEdit ) ]
        return actions
        
    def prepare_view(self, *args, **kw):
        """
        Add a few parameters for the view
        """
        super(UserAccountView, self).prepare_view(*args, **kw)
        self.account = self.useraccount
        self.n_communities = self.account and self.account.communities.count() or False
        self.n_network_members = self.account and self.account.network.count() or False

    def get_title(self,):
        return _("%(name)s's profile" % {'name': self.account.title} )  


class HomepageView(UserAccountView):
    """
    Special treatment for homepage.
    """
    is_home = True
    
    def get_title(self,):
        return _("Home")  
        
    def get_recent_content_list(self):
        """
        Retrieve recent content list for the given account.
        XXX TODO: Optimize this by adding a (first_twistable_on_home, last_twistable_on_home) values pair on the Account object.
        This way we can just query objects with id > last_twistable_on_home
        XXX TODO: Handle the anonymous users case!
        """
        latest_ids = Content.objects.followed
        latest_ids = latest_ids.order_by("-id").values_list('id', flat = True)[:settings.TWISTRANET_CONTENT_PER_PAGE]
        latest_list = Content.objects.__booster__.filter(id__in = tuple(latest_ids)).select_related(*self.select_related_summary_fields).order_by("-created_at")
        return latest_list
    
    def prepare_view(self, ):
        """
        We just have the account set as curently-auth account.
        """
        # Get the actual view instance. Not optimal, but, well, works.
        auth = Account.objects._getAuthenticatedAccount()
        if auth:
            return super(HomepageView, self).prepare_view(auth.id)
        else:
            raise NotImplementedError("XXX TODO: Handle anonymous access here.")


#                                                                               #
#                               LISTING VIEWS                                   #
#                                                                               #

class AccountListingView(BaseView):
    """
    Todo: account listing page
    """
    title = "Accounts"
    template = "account/list.html"
    template_variables = BaseView.template_variables + [
        "accounts",
    ]

    def prepare_view(self, ):
        super(AccountListingView, self).prepare_view()
        self.accounts = Account.objects.get_query_set()[:settings.TWISTRANET_COMMUNITIES_PER_PAGE]
        
        
class AccountNetworkView(UserAccountView):
    """
    All networked accounts for an account page
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables

    def get_title(self,):
        if self.account.id == Account.objects._getAuthenticatedAccount().id:
            return _("My network")
        return _("%(name)s's network" % {'name': self.account.title} )

    def prepare_view(self, *args, **kw):
        super(AccountNetworkView, self).prepare_view(*args, **kw)
        self.accounts = self.account.network


class PendingNetworkView(UserAccountView):
    """
    All pending network relations for an account
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables
    title = "Pending network requests"
    
    def get_title(self,):
        return _(self.title)

    def prepare_view(self):
        auth = Account.objects._getAuthenticatedAccount()
        super(PendingNetworkView, self).prepare_view(auth.id)
        self.accounts = self.account.get_pending_network_requests()


#                                                                               #
#                                   ACTION VIEWS                                #
#                                                                               #

class AddToNetworkView(BaseObjectActionView):
    """
    Add sbdy to my network, with or without authorization
    """
    model_lookup = UserAccount
    
    def as_action(self, request_view):
        """
        as_action(self, request_view) => generate the proper action
        """
        # Networking actions
        if request_view.useraccount.has_pending_network_request:
            return {
                "label": _("Accept in my network"),
                "url": reverse('add_to_my_network', args = (request_view.useraccount.id, ), ),
                "confirm": _("Would you like to accept %(name)s in your network? He/She will be able to see your network-only content." % {'name': request_view.useraccount.title}),
                "main": True,
            }
        if request_view.useraccount.can_add_to_my_network:
            return {
                "label": _("Add to my network"),
                "url": reverse('add_to_my_network', args = (request_view.useraccount.id, ), ),
                "confirm": _("Would you like to add %(name)s to your network? He/She will have to agree to your request." % {'name': request_view.useraccount.title}),
                "main": True,
            }
    
    def prepare_view(self, *args, **kw):
        super(AddToNetworkView, self).prepare_view(*args, **kw)
        self.redirect = self.useraccount.get_absolute_url()
        self.useraccount.add_to_my_network()
        name = self.useraccount.title
        if self.useraccount in self.auth.network:
            messages.info(
                self.request, 
                _("You're now connected with %(name)s." % {'name': name})
            )
        else:
            messages.info(
                self.request, 
                _("A network request has been sent to %(name)s for approval." % {'name': name})
            )
        

class RemoveFromNetworkView(BaseObjectActionView):
    """
    Add sbdy to my network, with or without authorization
    """
    model_lookup = UserAccount

    def as_action(self, request_view):
        if request_view.useraccount.has_received_network_request:
            return {
                "label": _("Cancel my network request"),
                "url": reverse('remove_from_my_network', args = (request_view.useraccount.id, ), ),
                "confirm": _("Would you like to cancel your network request?"),
            }
        if not request_view.auth_account.is_anonymous and not request_view.useraccount.id == request_view.auth_account.id:
            return {
                "label": _("Remove from my network"),
                "url": reverse('remove_from_my_network', args = (request_view.account.id, ), ),
                "confirm": _("Would you like to remove %(name)s from your network?" % {'name': request_view.account.title}),
            }        
        

    def prepare_view(self, *args, **kw):
        super(RemoveFromNetworkView, self).prepare_view(*args, **kw)
        self.redirect = self.useraccount.get_absolute_url()
        was_in_my_network = self.useraccount in self.auth.network
        self.useraccount.remove_from_my_network()
        name = self.useraccount.title
        if was_in_my_network:
            messages.info(
                self.request, 
                _("You're not connected with %(name)s anymore." % {'name': name})
            )
        else:
            messages.info(
                self.request, 
                _("Your network request to %(name)s has been canceled." % {'name': name})
            )


#                                                                           #
#                           Edition / Creation views                          #
#                                                                           #

class UserAccountEdit(UserAccountView):
    """
    Edit form for user account. Not so far from the view itself.
    """
    template = "account/edit.html"
    form_class = account_forms.UserAccountForm
    content_forms = []
    latest_content_list = []
    
    action_label = "Edit"
    action_reverse_url = "user_account_edit"
    
    def as_action(self, request_view):
        if not request_view.object.can_edit:
            return
        return super(UserAccountView, self).as_action(request_view)
    
    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if not self.object:
            return _("Create a user account")
        return _("Edit %(name)s" % {'name' : self.object.title })


class UserAccountCreate(UserAccountEdit):
    """
    UserAccount creation. Close to the edit class
    """
    context_boxes = []
    form_class = account_forms.UserAccountCreationForm
    
    






def account_logout(request):
    t = loader.get_template('registration/login.html')
    logout(request)
    c = RequestContext(
        request,
        {
            "justloggedout":True,
        },
        )
    return HttpResponse(t.render(c))

