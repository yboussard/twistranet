from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.http import urlquote
from twistranet import twistranet_settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings

class MustRedirect(Exception):
    """
    Raise this if something must redirect to the current page
    """
    pass


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
    
    @classmethod
    def as_view(cls, *args, **kw):
        return cls(*args, **kw)
    
    def view(self, request, *args, **kw):
        """
        It's up to you to override this method.
        """
        raise NotImplementedError("You must override this method")
        
        
    def __call__(self, request, *args, **kw):
        """
        Prepare the query, check various parameters and run it.
        """
        # Check if we have access to TN, if not we redirect to the login page.
        from twistranet.models import GlobalCommunity, AnonymousAccount
        mgr = GlobalCommunity.objects
        if not mgr.exists():
            path = urlquote(request.get_full_path())
            return HttpResponseRedirect('%s?%s=%s' % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path, ))
        
        # Render the view itself
        return self.view(request, *args, **kw)
        
    def get_important_action(self,):
        """
        Return the main action, emphased in the templates.
        Should return (label, url) or None if no emphased action available.
        The label will be translated in templates.
        """
        raise NotImplementedError
        
    def get_title(self, ):
        if self.title is None:
            raise NotImplementedError("You must override the title property in your derived view")
        return _(self.title)
        
    def get_breadcrumb(self,):
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
        
    def render_template(self, template, params):
        """
        Render the given template with the specified params (dict)...
        ...PLUS adds some parameters to provide better integration.
        """
        # Default parameters
        params['path'] = self.request.path
        params['context_boxes'] = self.context_boxes
        params['global_boxes'] = self.global_boxes
        params['title'] = self.get_title()
        params['breadcrumb'] = self.get_breadcrumb()
        
        # If we have a latest_content_list parameter, we can find some incitative ways of asking ppl to add more
        if params.has_key("latest_content_list"):
            if len(params['latest_content_list']) < (twistranet_settings.TWISTRANET_CONTENT_PER_PAGE / 2):
                # Just a half-page of content? Not enough!
                # TODO : Exclude notifications from this count
                params['too_few_content'] = True
        
        important_action = self.get_important_action()
        if important_action:
            params["important_action_label"], params["important_action_url"] = important_action
        t = get_template(template)
        c = RequestContext(self.request, params)
        return HttpResponse(t.render(c))
        
        
        