import copy
import re

from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.http import urlquote
from django.utils.safestring import mark_safe
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.shortcuts import get_object_or_404

from twistranet.twistranet.models import *
from twistranet.twistranet.forms import form_registry
from twistranet.twistranet.lib.log import *
from twistranet.twistranet.lib import utils

from twistranet.actions import *

class MustRedirect(Exception):
    """
    Raise this if something must redirect to the current page
    """
    def __init__(self, url = None):
        self.url = url
        super(MustRedirect, self).__init__(self, url)

class AsPublicView(object):
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
        
    def has_access(self):
        return True         # Can always access a public view
        
    def __call__(self, request, *args, **kw):
        """
        This generates the actual view instance.
        """
        try:
            # Check if we have access to TN, if not we redirect to the login page.
            if not self.has_access():
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
                redirect_url = request.path
            else:
                redirect_url = re.sub("^[a-zA-Z]+:\/\/(.*)(?=\/)", "", redirect.url)
            log.debug("Redirecting to %s" % redirect_url)
            return HttpResponseRedirect(redirect_url)
            
class AsView(AsPublicView):
    """
    Same as AsPublicView but for a (possibly) restricted view.
    """
    def has_access(self,):
        from twistranet.twistranet.models import GlobalCommunity, AnonymousAccount
        mgr = GlobalCommunity.objects
        return mgr.exists()
            
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
    available_actions = []      # List of either Action objects or BaseView classes (that will be instanciated and called with view.as_action() method)
    name = None                 # The name that this will be mapped to in url.py. But you can of course override this in url.py.
    # category = GLOBAL_ACTIONS   # Override this if you want to give another default category to this view.
    
    # The view attribute which will be passed to the templates
    template_variables = [
        ("title", "get_title"),
        "path",
        "context_boxes",
        "global_boxes",
        "breadcrumb",
    ]
    
    # Some implicit parameters will be passed. They are:
    # - actions: the list of actions defined for this view
    
    def __init__(self, request = None, other_view = None, ):
        """
        Instanciate a view, either from the main controller or from another view.
        In the latter case, the view is simply copied from the caller's view data.
        """
        # Check initial parameters
        if request and other_view:
            raise ValueError("You must instanciate either with a 'request' or 'other_view' parameter, but not both.")
        if not request and not other_view:
            raise ValueError("You must instanciate with either a 'request' or 'other_view' parameter.")
        
        # Check class consistancy
        if not self.name:
            raise ValueError("View class '%s' should have a name" % self.__class__)
        
        # Default parameters
        if request:
            self.request = request
            self.path = request and request.path
            
        if other_view:
            for param in self.template_variables:
                if isinstance(param, tuple):
                    continue        # Ignore function calls for the sake of simplicity
                if param in ("breadcrumb", ):
                    continue
                p = getattr(self, param, None)
                if callable(p):
                    continue
                # log.debug("%s %s" % (self, param))
                setattr(self, param, getattr(other_view, param, None))
                
    #                                                                                               #
    #                                       Actions Management                                      #
    #                                                                                               #
            
    def get_actions(self,):
        """
        Transform the available_actions list into an actions{} dict.
        """
        ret = {}
        flat_actions = []

        # Flatten the actions list
        for act in self.available_actions:
            if isinstance(act, Action):
                flat_actions.append(act)
            elif issubclass(act, BaseView):
                view_instance = act(other_view = self)
                as_action = view_instance.as_action()
                if isinstance(as_action, Action):
                    flat_actions.append(as_action)
                elif isinstance(as_action, list) or isinstance(as_action, tuple):
                    flat_actions.extend(as_action)
                elif as_action is None:
                    continue
                else:
                    raise ValueError("Invalid action type: %s for %s" % (as_action, act))
            
        for action in flat_actions:
            # Mark the confirm msg as html_safe
            if action.confirm:
                action.confirm = mark_safe(action.confirm)
            
            # Append it to the proper actions category
            if not ret.has_key(action.category.id):
                ret[action.category.id] = [ action ]
            else:
                ret[action.category.id].append(action)

        # Check that we've got only 1 main action at most
        if len(ret.get("main", [])) > 1:
            raise ValueError("More than 1 action in 'main' category: %s" % ret)
        return ret
            
    def as_action(self):
        """
        Default action management (for global views)
        """
        return Action(
            category = self.category,
            label = self.get_title(),
            url = reverse(self.name),
            confirm = getattr(self, "confirm", None),
        )
                
    def get_title(self, ):
        if self.title is None:
            raise NotImplementedError("You must override the title property or get_title() method in %s. Don't forget to _() your get_title() result!" % self.__class__)
        return _(self.title)
             
    @property           
    def breadcrumb(self,):
        """
        Return a list of (translated title, url) tuples. The first one should be the root.
        This method uses 2 ways of finding the breadcrumb path:
        - it inspects the menus to find if current view is specified somewhere (XXX TODO).
        - if not in the menus, we use publisher's information for content.
        - if not, it uses a good ol' stupid home > here scheme.
        """
        home_url = reverse("twistranet_home")
        home = (_("Home"), home_url, )
        here = (self.get_title(), self.request.path, )
        
        # The homepage: trivial case
        if self.request.path == home_url:
            return (home, )
            
        # XXX TODO: Menu management
            
        # Content: we preceed by the publisher
        elif hasattr(self, "object") and isinstance(self.object, Twistable) and issubclass(self.object.model_class, Content):
            pub = (self.object.publisher.title, self.object.publisher.get_absolute_url())
            return (home, pub, here)
            
        # Default case: home > here
        else:
            return (home, here, )
        
    def prepare_view(self):
        """
        Prepare all parameters before rendering the template.
        """
        pass

    def render_view(self, ):
        """
        Render the given template with the specified params (dict)...
        ...PLUS adds some parameters to provide better integration:
        - actions
        - current_account
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
            
        # Generate actions and other params
        params["actions"] = self.get_actions()
        params["current_account"] = Twistable.objects.getCurrentAccount(self.request)
        params["site_name"] = utils.get_site_name()
        params["baseline"] = utils.get_baseline()
        
        # Render template
        t = get_template(self.template)
        c = RequestContext(self.request, params)
        return HttpResponse(t.render(c))
                

class BaseIndividualView(BaseView):
    """
    A view for an individual object.
    Edition works too!
    Lookup is performed on the object, so that the view is called with its object already set.
    We only use a 'lookup' parameter which is used to set the lookup attribute.
    Just define a model_lookup parameter below. The variable holding the object
    will be model_lookup.__name__.lower().
    """
    model_lookup = None
    form_class = None               # If set, will be used to generate a form for the view
    redirect = None

    def __init__(self, request = None, other_view = None, lookup = "id"):
        """
        The individual views take a lookup argument specifying on which attribute
        we'll check the individual model object.
        """
        # Call parent's init
        super(BaseIndividualView, self).__init__(request, other_view)
        
        # Explicitly set 'object' if it's set on the other_view
        if other_view:
            object = getattr(other_view, 'object', None)
            if object:
                setattr(self, "object", object)
        
        # Check if everything is working
        if self.model_lookup is None:
            raise RuntimeError("You must define a model_lookup attribute in your view class specifying the model you want to read the object from")
        self.lookup = lookup
        
    def get_form_class(self,):
        """
        You can use self.request and self.object to find your form here
        if you need to determinate it with an acute precision.
        """
        return self.form_class
        
    def prepare_view(self, value = None, ):
        """
        Fetch the individual object.
        'value' is the value used to fetch the object.
        """
        # Prepare specific parameters
        self.auth = Account.objects._getAuthenticatedAccount()
        if value:
            q_param = { self.lookup: value }
            if self.model_lookup is None:
                raise RuntimeError("You must specify a model lookup in your subclass %s" % self.__class__.__name__)
            obj = get_object_or_404(self.model_lookup, **q_param)
        else:
            obj = None
        self.object = obj and obj.object
        model_name = self.model_lookup.__name__.lower()
        
        # If we have a form (ie. self.form_class or self.get_form_class available), process form
        form_class = self.get_form_class()
        if form_class:
            setattr(self, model_name, self.object)
            self.template_variables = self.template_variables + ["form", ]
            if self.request.method == 'POST': # If the form has been submitted...
                self.form = form_class(self.request.POST, self.request.FILES, instance = self.object)
                publisher_id = self.request.POST.get('publisher_id', None)
                if publisher_id:
                    publisher = Account.objects.get(id = publisher_id)    # Will raise if unauthorized
                else:
                    publisher = None
                if self.form.is_valid(): # All validation rules pass
                    # Save object and set publisher
                    self.object = self.form.save(commit = False)
                    if publisher:
                        self.object.publisher = publisher
                    self.object.save()
                    self.form.save_m2m()
                    raise MustRedirect(self.object.get_absolute_url())
            else:
                if self.object:
                    self.form = form_class(instance = self.object)      # An unbound form with an explicit instance
                else:
                    initial = self.get_initial_values()
                    if initial:
                        self.form = form_class(initial = initial)
                    else:
                        self.form = form_class()

        # Various data. Call parent LAST.
        setattr(self, model_name, self.object)
        super(BaseIndividualView, self).prepare_view()

    def get_initial_values(self,):
        """
        Return initial values for the form data
        """
        return getattr(self, "initial", None)

    def as_action(self):
        """
        Default action management
        """
        confirm = getattr(self, "confirm", None)
        if confirm:
            confirm = mark_safe(_(confirm))
        return Action(
            category = getattr(self, "category", LOCAL_ACTIONS),
            label = self.get_title(),
            url = reverse(self.name, args = (self.object.id, ), ),
            confirm = confirm,
        )

    @property
    def is_model(self,):
        """
        Check if the current action matches the model.
        """
        if not hasattr(self, "object"):
            return False
        if not isinstance(self.object, self.model_lookup):
            return False
        return True
        

class BaseObjectActionView(BaseIndividualView):
    """
    A view that does something and then redirects to somewhere else.
    Just overload the prepare_view method with what you have to do.
    
    If you set the redirect attribute, it will redirect there.
    """
    def render_view(self,):
        # If we ever reach there, we return to redirect attribute.
        if self.redirect is None:
            raise NotImplementedError("Should implement a default redirecting scheme")
        raise MustRedirect(self.redirect)

        
class BaseWallView(BaseIndividualView):
    """
    A wall has a latest_content_list parameter
    """
    template_variables = BaseIndividualView.template_variables + [
        "content_forms",
        "latest_content_list",
    ]

    select_related_summary_fields = (
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
        if not self.auth or self.auth.is_anonymous:
            return []       # Anonymous can't do that much things...
        if not publisher:
            publisher = self.auth

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
                form = form_class(self.request.POST, self.request.FILES, initial = initial)
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
    
    def prepare_view(self, value = None):
        """
        Fetch the individual object, plus its latest content.
        """
        super(BaseWallView, self).prepare_view(value)
        # if self.object:
        self.latest_content_list = self.get_recent_content_list()
        self.content_forms = self.get_inline_forms(self.object)
        
        
        
        
        