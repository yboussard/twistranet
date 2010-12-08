import copy
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.http import urlquote
from twistranet import twistranet_settings
from twistranet.models import *
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.shortcuts import get_object_or_404
from twistranet.lib import form_registry


class MustRedirect(Exception):
    """
    Raise this if something must redirect to the current page
    """
    def __init__(self, url = None):
        self.url = url
        super(MustRedirect, self).__init__(self, url)

class AsView(object):
    """
    A wrapper around an actual View Instance class.
    
    In your urls: AsView(AccountView, lookup = 'id')
    """
    def __init__(self, view_instance_class, *args, **kw):
        """
        Save arguments for later use
        """
        self.view_instance_class = view_instance_class
        self.args = args
        self.kw = kw
        
    def __call__(self, request, *args, **kw):
        """
        This generates the actual view instance.
        """
        try:
            # Check if we have access to TN, if not we redirect to the login page.
            from twistranet.models import GlobalCommunity, AnonymousAccount
            mgr = GlobalCommunity.objects
            if not mgr.exists():
                path = urlquote(request.get_full_path())
                raise MustRedirect('%s?%s=%s' % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path, ))

            # Instanciate the actual view class with global view arguments
            # and call its view() method with request-specific arguments
            instance_view = self.view_instance_class(request, *self.args, **self.kw)
            instance_view.prepare_view(*args, **kw)
            return instance_view.render_view()
            
        except MustRedirect as redirect:
            # Here we redirect if necessary
            if redirect.url is None:
                redirect.url = request.path
            return HttpResponseRedirect(redirect.url)
            
class BaseView(object):
    """
    This is used as a foundation for our classical views.
    You can define for each class which are the boxes used on it.
    Just overload the view() method in your classes.
    
    Default behaviour is to block access to non-authorized ppl (ppl who can't access GlobalCommunity).
    XXX I SHOULD OPTIMIZE THIS, BTW (avoiding an unnecessary query?)
    """
    # Overload those properties in your base classes
    context_boxes = []
    title = None        # Use this as a title or overload get_title() to use a context-dependant title
    global_boxes = [
        "actions/general.part.html",
        "content/content_creation.box.html",
    ]
    view_template = None
    
    # The view attribute which will be passed to the templates
    template_variables = [
        ("title", "get_title"),
        "path",
        "context_boxes",
        "global_boxes",
        "breadcrumb",
        ("actions", "get_actions", )
    ]    
    
    def get_actions(self,):
        """
        Return the main action, emphased in the templates.
        Should return a list of dicts with the following keys :
        - label (TRANSLATED)
        - URL
        - main as a boolean (assumed as False if absent). Only 1 main action is possible.
        
        Default is to return the self.actions object attribute.
        The get_actions method is called in the last process before rendering, so your intermediate
        methods can safely add stuff to the self.actions list.
        """
        return getattr(self, "actions", [])
        
    def get_title(self, ):
        if self.title is None:
            raise NotImplementedError("You must override the title property in your derived view. Don't forget to _() your title!")
        return _(self.title)
             
    @property           
    def breadcrumb(self,):
        """
        Return a list of (translated title, url) tuples. The first one should be the root.
        This method uses 2 ways of finding the breadcrumb path:
        - it inspects the menus to find if current view is specified somewhere (XXX TODO)
        - if not, it uses a good ol' stupid home > here scheme.
        """
        home_url = reverse("twistranet_home")
        home = (_("Home"), home_url, )
        if not self.request.path == home_url:
            here = (self.get_title(), self.request.path, )
            return (home, here, )
        else:
            return (home, )
        
    def __init__(self, request):
        self.request = request
        self.path = request.path
        
    def prepare_view(self):
        """
        Prepare all parameters before rendering the template.
        """
        pass

    def render_view(self, ):
        """
        Render the given template with the specified params (dict)...
        ...PLUS adds some parameters to provide better integration.
        """
        # Populate parameters
        params = {}
        for param in self.template_variables:
            if isinstance(param, tuple):
                k, attr = param
            else:
                k = attr = param
            if params.has_key(k):
                continue
            v = getattr(self, attr)
            if callable(v):
                v = v()
            params[k] = v
            
        # Generate actions
        actions = self.get_actions()
        main = [ a for a in actions if a.get('main', False) ]
        if len(main) > 1:
            raise ValueError("Several main actions for %s: %s" % (self, main, ))
        if main:
            params["main_action"] = main[0]
        params["actions"] = [ a for a in actions if not a.get('main', False) ]
        
        # Render template
        t = get_template(self.template)
        c = RequestContext(self.request, params)
        return HttpResponse(t.render(c))
        

class BaseRedirectView(BaseView):
    """
    A view that does something and then redirects to somewhere else.
    Just overload the prepare_view method and raise a MustRedirect exception when you're done.
    """
    default_redirect = "twistranet_home"
    
    def prepare_view(self, *args, **kw):
        raise NotImplementedError("You must implement this.")
        
    def render_view(self,):
        # If we ever reach there, we return to default_redirect
        raise MustRedirect(reverse(self.default_redirect))


class BaseIndividualView(BaseView):
    """
    A view for an individual object. Lookup is performed on the object,
    so that the view is called with its object already set.
    We only use a 'lookup' parameter which is used to set the lookup attribute.
    Just define a model_lookup parameter below. The variable holding the object
    will be model_lookup.__name__.lower().
    """
    model_lookup = None
    is_home = False

    def __init__(self, request, lookup = "id"):
        """
        The individual views take a lookup argument specifying on which attribute
        we'll check the individual model object.
        """
        # Call parent's init
        super(BaseIndividualView, self).__init__(request)
        
        # Check if everything is working
        if self.model_lookup is None:
            raise RuntimeError("You must define a model_lookup attribute in your view class specifying the model you want to read the object from")
        self.lookup = lookup
        
    def prepare_view(self, value, ):
        """
        Fetch the individual object.
        """
        # Prepare specific parameters
        q_param = { self.lookup: value }
        if self.model_lookup is None:
            raise RuntimeError("You must specify a model lookup in your subclass %s" % self.__class__.__name__)
        obj = get_object_or_404(self.model_lookup, **q_param)
        self.object = obj
        setattr(self, self.model_lookup.__name__.lower(), obj)
        super(BaseIndividualView, self).prepare_view()
        
        # Check if URL is ok; If not, redirect to the absolute_url view
        # if not self.is_home and not self.request.path.startswith(obj.get_absolute_url()):
        #     raise MustRedirect(obj.get_absolute_url())
        
class BaseWallView(BaseIndividualView):
    """
    A wall has a latest_content_list parameter
    """
    template_variables = BaseIndividualView.template_variables + [
        "content_forms",
        "latest_content_list",
        "too_few_content",
    ]

    too_few_content = False

    # XXX For some obscure reason, I've got a dirty django error when trying to select_related content_types.
    # I have to find how and why... but perhaps subtypes are not needed in account page, thanks to the xxx_summary/xxx_headline fields?
    select_related_summary_fields = (
        # "notification",
        # "statusupdate",
        "owner",
        "publisher",
    )

    def get_inline_forms(self, publisher = None):
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
    
    def get_recent_content_list(self):
        """
        Retrieve recent content list for the given account.
        XXX TODO: Optimize this by adding a (first_twistable_on_home, last_twistable_on_home) values pair on the Account object.
        This way we can just query objects with id > last_twistable_on_home
        """
        latest_ids = Content.objects.getActivityFeed(self.object)    
        latest_ids = latest_ids.order_by("-id").values_list('id', flat = True)[:twistranet_settings.TWISTRANET_CONTENT_PER_PAGE]
        latest_list = Content.objects.__booster__.filter(id__in = tuple(latest_ids)).select_related(*self.select_related_summary_fields).order_by("-created_at")
        return latest_list

    def prepare_view(self, value):
        """
        Fetch the individual object, plus its latest content
        """
        super(BaseWallView, self).prepare_view(value)
        self.latest_content_list = self.get_recent_content_list()
        if len(self.latest_content_list) < (twistranet_settings.TWISTRANET_CONTENT_PER_PAGE / 2):
            self.too_few_content = True
        self.content_forms = self.get_inline_forms(self.object)
        