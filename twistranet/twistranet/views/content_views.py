# Create your views here.
#from django.template import Context, RequestContext, loader
#from django.http import HttpResponse, HttpResponseRedirect
#from django.template.loader import get_template
#from django.contrib.auth.decorators import login_required
#from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
#from django.db.models import Q
from django.shortcuts import *
from django.contrib import messages
from django.utils.translation import ugettext as _
#from twistranet.twistranet.lib.decorators import require_access

from twistranet.twistranet.models import Content, Account
from twistranet.twistranet.forms import form_registry
from base_view import *

class ContentView(BaseIndividualView):
    """
    Individual Content View.
    """
    context_boxes = [
        'content/publisher.box.html',    
        'actions/context.box.html', 
        'content/metadata.box.html', 
    ]
    template = None  # Will be overridden later
    template_variables = BaseIndividualView.template_variables + [
        "content",
    ]
    model_lookup = Content
        
    def get_title(self,):
        return self.content.title_or_description
        
    def get_actions(self,):
        """
        Basic actions on communities
        """
        actions = []
        if not self.content:
            return []
        
        # Contributor stuff
        if self.content.can_edit:
            actions.append({
                "label": _("Edit content"),
                "url": reverse("edit_content", args = (self.content.id, )),
            })
    
        return actions

    def prepare_view(self, *args, **kw):
        """
        Prepare community view.
        Special funny thing here: we replace content by its actual underlying object.
        This is so because of the proheminence of the 'content.text' property we won't be able to fetch otherwise.
        """
        super(ContentView, self).prepare_view(*args, **kw)
        self.content = self.content and self.content.object
        if not self.template:
            self.template = self.content.detail_view


class ContentEdit(ContentView):
    """
    Generic edit form for content.
    """
    template = "content/edit.html"

    def get_form_class(self,):
        if self.object:
            ctype = self.object.model_name
        else:
            ctype = self.content_type
        try:
            return form_registry.getFormEntries(ctype, edition = True)[0]['form_class']
        except IndexError:
            raise ValueError("No Form registered for this content type: '%s'" % ctype)

    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if not self.object:
            return _("New content")
        return _("Edit %(name)s" % {'name' : self.object.title_or_description })


class ContentCreate(ContentEdit):
    """
    Community creation. Close to the edit class
    """
    context_boxes = []

    def prepare_view(self, content_type):
        """
        We pass the content_type instead of the value
        """
        self.content_type = content_type
        super(ContentCreate, self).prepare_view(None)

class ContentDelete(BaseObjectActionView):
    """
    Remove a content from the base
    """
    model_lookup = Content

    def prepare_view(self, *args, **kw):
        super(ContentDelete, self).prepare_view(*args, **kw)
        self.redirect = self.content.publisher.get_absolute_url()
        name = self.content.title_or_description
        self.content.delete()
        messages.info(
            self.request, 
            _("'%(name)s' has been deleted." % {'name': name})
        )



