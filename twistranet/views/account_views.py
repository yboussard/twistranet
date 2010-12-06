# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django.utils.translation import ugettext as _

from twistranet.models import *
from twistranet.lib import form_registry
from twistranet.lib.decorators import require_access
from django.shortcuts import get_object_or_404
from twistranet import twistranet_settings
from base_view import BaseView

# XXX For some obscure reason, I've got a dirty django error when trying to select_related content_types.
# I have to find how and why... but perhaps subtypes are not needed in account page, thanks to the xxx_summary/xxx_headline fields?
select_related_summary_fields = (
    # "notification",
    # "statusupdate",
    "owner",
    "publisher",
)

class MustRedirect(Exception):
    """
    Raise this if something must redirect to the current page
    """
    pass


class BaseAccountView(BaseView):
    """
    This is what is used as a base view for accounts
    """
    context_boxes = [
        'account/profile.box.html',
        'account/actions.box.html',
        'account/relations.box.html',
    ]
    
    important_action = None
    
    def get_important_action(self):
        """Propose to join"""
        return self.important_action
    
    def _getInlineForms(self, publisher = None):
        """
        - a forms list ; empty list if no form to display ;

        Return the inline forms object used to display the marvellous edition form(s).
        Process 'em, by the way.
        'publisher' is the account we're going to publish on. If none, assume it's the current user.
        """
        # Account information used to build the wall view
        account = Account.objects._getAuthenticatedAccount()
        if not account or account.is_anonymous:
            return []       # Anonymous can't do that much things...
        if not publisher:
            publisher = account

        # Wall edition forms if user has the right to write on it
        # This return a list of forms as each content type can define its own tab+form
        form_classes = form_registry.getInlineForms(publisher)
        forms = []
        for form_class in [ k['form_class'] for k in form_classes ]:
            # Initial data processing
            initial = {
                "publisher_id": publisher.id,
                "publisher":    publisher,
                }

            # Form display / validation stuff
            if self.request.method != 'POST':                        # If the form has not been submitted...
                form = form_class(initial = initial)
                forms.append(form)
            else:                                               # Ok, we submited
                form = form_class(self.request.POST, initial = initial)
                content_type = form.getName()

                # We skip validation for forms of other content types.
                if self.request.POST.get('validated_form', None) <> content_type:
                    forms.append(form_class(initial = initial))
                    continue

                # Validate stuff
                if form.is_valid():                             # All validation rules pass
                    # Process the data in form.cleaned_data
                    c = form.save(commit = False)
                    c.publisher = Account.objects.get(id = self.request.POST.get('publisher_id'))    # Will raise if unauthorized
                    c.save()
                    form.save_m2m()
                    # forms.append(form_class(initial = initial)) => Silly stuff anyway?
                    raise MustRedirect()
                else:
                    forms.append(form)

        # Return the forms
        return forms

    def get_recent_content_list(self, acc):
        """
        Retrieve recent content list for the given account.
        XXX TODO: Optimize this by adding a (first_twistable_on_home, last_twistable_on_home) values pair on the Account object.
        This way we can just query objects with id > last_twistable_on_home
        """
        if acc == Account.objects._getAuthenticatedAccount():
            latest_ids = Content.objects.followed
        else:
            latest_ids = Content.objects.getActivityFeed(acc)
            
        latest_ids = latest_ids.order_by("-id").values_list('id', flat = True)[:twistranet_settings.TWISTRANET_CONTENT_PER_PAGE]
        latest_list = Content.objects.__booster__.filter(id__in = tuple(latest_ids)).select_related(*select_related_summary_fields).order_by("-created_at")
        return latest_list

    def account_view(self, account, ):
        """
        Account (user/profile) page.
        We just diplay posts of any given account.
        XXX TODO:
            - Check if account is listed and permit only if approved
        """
        # If we're on a community, we should redirect
        if isinstance(account, Community):
            return HttpResponseRedirect(account.get_absolute_url())

        # Generate forms and ensure proper redirection if applicable
        try:
            forms = self._getInlineForms(publisher = account)
        except MustRedirect:
            return HttpResponseRedirect(self.request.path)
        
        # Generate the view itself
        auth_account = Account.objects._getAuthenticatedAccount()
        in_my_network = auth_account.network.filter(id = account.id)
        if not in_my_network and not auth_account.is_anonymous:
            self.important_action = ("Add to my network", "twistranet_home")
        
        # Return the template with its parameters
        return self.render_template(
            "account/view.html",
            {
                "path": self.request.path,
                "content_forms": forms,
                "account": account,
                "latest_content_list": self.get_recent_content_list(account),
                "can_add_to_my_network": not auth_account.is_anonymous and not auth_account.id == account.id and not in_my_network,
                "can_remove_from_my_network": not auth_account.is_anonymous and not auth_account.id == account.id and in_my_network,
            })
    
class AccountView(BaseAccountView):
    """
    A regular account page
    """
    def get_title(self,):
        return _("%s's profile" % self.account.text_headline)
    
    @classmethod
    def as_view(cls, lookup = "id"):
        obj = cls()
        obj.lookup = lookup
        return obj
    
    def view(self, request, value):
        self.request = request
        param = { self.lookup: value }
        self.account = get_object_or_404(Account, **param)
        if not self.account.get_absolute_url() == self.request.path:
            # We're not on the actual URL for this object => we redirect to the actual absolute url
            return HttpResponseRedirect(self.account.get_absolute_url())
        return self.account_view(self.account)

class HomepageView(BaseAccountView):
    """
    Special treatment for homepage.
    """
    title = "Home"
    
    def get_important_action(self):
        """Nothing really critical in the homepage"""
        return None
    
    def view(self, request):
        self.request = request
        account = Account.objects._getAuthenticatedAccount()
        return self.account_view(account)

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

