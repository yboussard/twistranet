# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.utils.translation import ugettext as _

from twistranet.models import *
from twistranet import twistranet_settings
from base_view import BaseView, BaseIndividualView, BaseWallView, MustRedirect




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
        auth_account = Account.objects._getAuthenticatedAccount()
        in_my_network = auth_account.network.filter(id = self.account.id)
        if not in_my_network and not auth_account.is_anonymous and not self.account.id == auth_account.id:
            actions.append({
                "label": _("Add to my network"),
                "url": reverse('add_to_my_network', args = (self.account.id, ), ),
                "confirm": _("Would you like to add %(name)s to your network? He will have to agree to your request." % {'name': self.account.text_summary}),
                "main": True,
            })
        if in_my_network and not auth_account.is_anonymous and not self.account.id == auth_account.id:
            actions.append({
                "label": _("Remove from my network"),
                "url": reverse('remove_from_my_network', args = (self.account.id, ), ),
                "confirm": _("Would you like to remove %(name)s from your network?" % {'name': self.account.text_summary}),
            })
        return actions
        
    def prepare_view(self, *args, **kw):
        """
        Add a few parameters for the view
        """
        super(UserAccountView, self).prepare_view(*args, **kw)
        self.account = self.useraccount
        self.n_communities = self.account.communities.count()
        self.n_network_members = self.account.network.count()

    def get_title(self,):
        return _("%(name)s's profile" % {'name': self.account.text_headline} )  


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
        latest_ids = latest_ids.order_by("-id").values_list('id', flat = True)[:twistranet_settings.TWISTRANET_CONTENT_PER_PAGE]
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
        self.accounts = Account.objects.get_query_set()[:twistranet_settings.TWISTRANET_COMMUNITIES_PER_PAGE]
        
        
class AccountNetworkView(UserAccountView):
    """
    All communities for an account page
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables

    def get_title(self,):
        if self.account.id == Account.objects._getAuthenticatedAccount().id:
            return _("My network")
        return _("%(name)s's network" % {'name': self.account.text_headline} )

    def prepare_view(self, *args, **kw):
        super(AccountNetworkView, self).prepare_view(*args, **kw)
        self.accounts = self.account.network



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

