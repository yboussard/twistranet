# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.conf import settings

from twistranet.twistranet.models import *
from twistranet.twistranet.forms import account_forms
from twistranet.actions import *
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
    ]
    
    model_lookup = UserAccount
    template = "account/view.html"
    title = None
    name = "account_by_id"
    
    def prepare_view(self, *args, **kw):
        """
        Add a few parameters for the view
        """
        # Regular creation
        super(UserAccountView, self).prepare_view(*args, **kw)
        self.account = self.useraccount
        self.n_communities = self.account and self.account.communities.count() or False
        self.n_network_members = self.account and self.account.network.count() or False
        
        # Add a message for ppl who have no content
        auth = Twistable.objects.getCurrentAccount(self.request)
        if self.account and auth and self.account.id == auth.id:
            if not Content.objects.filter(publisher = auth).exists():
                messages.info(self.request, _("""<p>
                    It seems that you do not have created content yet. Maybe it's time to do so!
                    </p>
                    <p>
                    Creating content in twistranet is easy. For example, just tell what you're working on in the form below and click the "Send" button.
                    </p>
                    <p>
                    Want to learn about what you can do in twistranet? Just take a look here: [help]
                    </p>
                """))

    def get_title(self,):
        """
        We override get_title in a way that it could be removed easily in subclasses.
        Just define a valid value for self.title and this get_title() will keep the BaseView behaviour
        """
        if not self.title:
            return _("%(name)s's profile" % {'name': self.account.title} )
        return super(UserAccountView, self).get_title()


class HomepageView(UserAccountView):
    """
    Special treatment for homepage.
    """
    name = "twistranet_home"
    
    def get_title(self,):
        return _("Timeline")  
        
    def get_recent_content_list(self):
        """
        Retrieve recent content list for the given account.
        XXX TODO: Optimize this by adding a (first_twistable_on_home, last_twistable_on_home) values pair on the Account object.
        This way we can just query objects with id > last_twistable_on_home
        """
        auth = Account.objects._getAuthenticatedAccount()
        latest_ids = Content.objects
        if not auth.is_anonymous:
            if Content.objects.filter(publisher = auth).exists():
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
        if not auth.is_anonymous:
            prep_id = auth.id
        else:
            prep_id = None
        super(HomepageView, self).prepare_view(prep_id)

class PublicTimelineView(UserAccountView):
    name = "timeline"
    title = "Public timeline"
    
    def get_recent_content_list(self):
        """
        Just return all public / available content
        """
        latest_ids = Content.objects.order_by("-id").values_list('id', flat = True)[:settings.TWISTRANET_CONTENT_PER_PAGE]
        latest_list = Content.objects.__booster__.filter(id__in = tuple(latest_ids)).select_related(*self.select_related_summary_fields).order_by("-created_at")
        return latest_list

#                                                                               #
#                               LISTING VIEWS                                   #
#                                                                               #

class AccountListingView(BaseView):
    """
    Todo: ALL accounts listing page.
    """
    title = "Accounts"
    template = "account/list.html"
    template_variables = BaseView.template_variables + [
        "accounts",
    ]

    def prepare_view(self, ):
        super(AccountListingView, self).prepare_view()
        self.accounts = Account.objects.get_query_set()[:settings.TWISTRANET_COMMUNITIES_PER_PAGE]
        
        
class AccountNetworkView(AccountListingView, UserAccountView):
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
        super(AccountNetworkView, self).prepare_view()
        UserAccountView.prepare_view(self, *args, **kw)
        self.accounts = self.account.network   


class AccountCommunitiesView(AccountListingView, UserAccountView):
    """
    All communities for an account.
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables

    def get_title(self,):
        if self.account.id == Account.objects._getAuthenticatedAccount().id:
            return _("My communities")
        return _("%(name)s's communities" % {'name': self.account.title} )

    def prepare_view(self, *args, **kw):
        super(AccountCommunitiesView, self).prepare_view()
        UserAccountView.prepare_view(self, *args, **kw)
        self.accounts = self.account.communities    


class AccountAdminCommunitiesView(AccountListingView, UserAccountView):
    """
    All communities administred by an account.
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables

    # XXX TODO
    
    def get_title(self,):
        if self.account.id == Account.objects._getAuthenticatedAccount().id:
            return _("My communities")
        return _("%(name)s's communities" % {'name': self.account.title} )

    def prepare_view(self, *args, **kw):
        super(AccountCommunitiesView, self).prepare_view(*args, **kw)
        UserAccountView.prepare_view(self, *args, **kw)
        self.accounts = self.account.communities


class PendingNetworkView(AccountListingView, UserAccountView):
    """
    All pending network relations for an account
    """
    template = AccountListingView.template
    template_variables = UserAccountView.template_variables + AccountListingView.template_variables
    title = "Pending network requests"
    name = "account_pending_network"
    category = ACCOUNT_ACTIONS
    
    def as_action(self,):
        """Only return the action if there's pending nwk requests
        """
        auth = UserAccount.objects._getAuthenticatedAccount()
        req = auth.get_pending_network_requests()
        if not req:
            return
        action = BaseView.as_action(self)
        action.label = mark_safe(_('<span class="badge">%(number)d</span> Pending network requests') % {"number": len(req)})
        return action
            
    def prepare_view(self, *args, **kw):
        auth = Account.objects._getAuthenticatedAccount()
        super(PendingNetworkView, self).prepare_view()
        UserAccountView.prepare_view(self, auth.id)
        self.accounts = self.account.get_pending_network_requests()


#                                                                               #
#                                   ACTION VIEWS                                #
#                                                                               #

class AddToNetworkView(BaseObjectActionView):
    """
    Add sbdy to my network, with or without authorization
    """
    model_lookup = UserAccount
    name = "add_to_my_network"
    
    def as_action(self, ):
        """
        as_action(self, ) => generate the proper action.
        """
        if not hasattr(self, "object"):
            return None
        if not isinstance(self.object, UserAccount):
            return None
        
        # Networking actions
        if self.object.has_pending_network_request:
            return Action(
                label = _("Accept in my network"),
                url = reverse(self.name, args = (self.object.id, ), ),
                confirm = _(
                    "Would you like to accept %(name)s in your network?<br />"
                    "He/She will be able to see your network-only content."
                    ) % { "name": self.object.title },
                category = MAIN_ACTION,
            )
                            
        elif self.object.can_add_to_my_network:
            return Action(
                label = _("Add to my network"),
                url = reverse(self.name, args = (self.object.id, ), ),
                confirm = _(
                    "Would you like to add %(name)s to your network?<br />"
                    "He/She will have to agree to your request."
                    ) % {"name": self.object.title},
                category = MAIN_ACTION,
            )
    
    def prepare_view(self, *args, **kw):
        super(AddToNetworkView, self).prepare_view(*args, **kw)
        self.redirect = self.useraccount.get_absolute_url()
        self.useraccount.add_to_my_network()
        name = self.useraccount.title
        if self.useraccount in self.auth.network:
            messages.success(
                self.request, 
                _("You're now connected with %(name)s.") % {'name': name}
            )
        else:
            messages.info(
                self.request, 
                _("A network request has been sent to %(name)s for approval.") % {'name': name}
            )
        

class RemoveFromNetworkView(BaseObjectActionView):
    """
    Add sbdy to my network, with or without authorization
    """
    model_lookup = UserAccount
    name = "remove_from_my_network"

    def as_action(self, ):
        if not isinstance(getattr(self, "object", None), self.model_lookup):
            return None
        if self.object.has_received_network_request:
            return Action(
                category = LOCAL_ACTIONS,
                label = _("Cancel my network request"),
                url = reverse(self.name, args = (self.object.id, ), ),
                confirm = _("Would you like to cancel your network request?"),
            )
        if self.object.in_my_network:
            return Action(
                category = LOCAL_ACTIONS,
                label = _("Remove from my network"),
                url = reverse(self.name, args = (self.object.id, ), ),
                confirm = _("Would you like to remove %(name)s from your network?") % {"name": self.object.title},
            )

    def prepare_view(self, *args, **kw):
        super(RemoveFromNetworkView, self).prepare_view(*args, **kw)
        self.redirect = self.useraccount.get_absolute_url()
        was_in_my_network = self.useraccount in self.auth.network
        self.useraccount.remove_from_my_network()
        name = self.useraccount.title
        if was_in_my_network:
            messages.success(
                self.request, 
                _("You're not connected with %(name)s anymore.") % {'name': name}
            )
        else:
            messages.info(
                self.request, 
                _("Your network request to %(name)s has been canceled.") % {'name': name}
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
    name = "user_account_edit"
    category = LOCAL_ACTIONS
    
    def as_action(self,):
        """
        Return action only if can_edit user
        """
        if not self.is_model:
            return None
        if self.object.can_edit:
            return super(UserAccountEdit, self).as_action()
    
    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if not self.object:
            return _("Create a user account")
        elif self.object.id == UserAccount.objects._getAuthenticatedAccount().id:
            return _("Edit my account")
        return _("Edit %(name)s" % {'name' : self.object.title })


class UserAccountCreate(UserAccountEdit):
    """
    UserAccount creation. Close to the edit class
    """
    context_boxes = []
    form_class = account_forms.UserAccountCreationForm
    

class AccountLogin(BaseView):
    template = "registration/login.html"
    name = "login"
    title = "Login"
    template_variables = BaseView.template_variables + \
        ['form', 'site', 'next', ]
    
    def prepare_view(self,):
        """
        request, template_name='registration/login.html',
              redirect_field_name=REDIRECT_FIELD_NAME,
              authentication_form=AuthenticationForm):
        Displays the login form and handles the login action.
        this is from django.contrib.auth.views
        """
        from django.contrib.auth.views import REDIRECT_FIELD_NAME as redirect_field_name        # = 'next'
        from django.contrib.auth.views import AuthenticationForm as authentication_form
        from django.contrib.auth.views import auth_login
        from django.contrib.sites.models import Site, RequestSite
        redirect_to = self.request.REQUEST.get(redirect_field_name, '')

        if self.request.method == "POST":
            self.form = authentication_form(data=self.request.POST)
            if self.form.is_valid():
                # Light security check -- make sure redirect_to isn't garbage.
                if not redirect_to or ' ' in redirect_to:
                    redirect_to = settings.LOGIN_REDIRECT_URL

                # Heavier security check -- redirects to http://example.com should 
                # not be allowed, but things like /view/?param=http://example.com 
                # should be allowed. This regex checks if there is a '//' *before* a
                # question mark.
                elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                    redirect_to = settings.LOGIN_REDIRECT_URL

                # Okay, security checks complete. Log the user in.
                auth_login(self.request, self.form.get_user())
                setattr(self, redirect_field_name, redirect_to)    
                if self.request.session.test_cookie_worked():
                    self.request.session.delete_test_cookie()
                raise MustRedirect(redirect_to)
            else:
                # Invalid user/password
                messages.warning(self.request, _("Sorry, that's not a valid username or password"))
        else:
            self.form = authentication_form(self.request)

        self.request.session.set_test_cookie()

        if Site._meta.installed:
            self.site = Site.objects.get_current()
        else:
            self.site = RequestSite(self.request)
        setattr(self, redirect_field_name, redirect_to)
    
    
class AccountLogout(BaseView):
    template = "registration/login.html"
    template_variables = BaseView.template_variables + ["justloggedout", ]
    name = "logout"
    title = "Logged out"

    def prepare_view(self,):
        messages.info(self.request, _("You are now logged out.<br />Thanks for spending some quality time on Twistranet."))
        self.justloggedout = True
        logout(self.request)





