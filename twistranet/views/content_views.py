# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.shortcuts import *
from django.contrib import messages
from django.utils.translation import ugettext as _
from twistranet.lib.decorators import require_access

from twistranet.models import Content, Account
from twistranet.lib import form_registry
from base_view import *




class ContentView(BaseIndividualView):
    """
    Individual Content View.
    """
    context_boxes = [
        'content/metadata.box.html',
        'actions/context.box.html',
    ]
    template = "content/view.html"
    template_variables = BaseIndividualView.template_variables + [
        "content",
    ]
    model_lookup = Content
        
    def get_title(self,):
        return self.content.text_headline
        
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


class ContentEdit(ContentView):
    """
    Generic edit form for content.
    """
    template = "content/edit.html"

    def get_form_class(self,):
        if self.object:
            return form_registry.getFormEntries(self.object.model_name, edition = True)[0]['form_class']
        else:
            return form_registry.getFormEntries(self.content_type, creation = True)[0]['form_class']
            

    def get_title(self,):
        """
        Title suitable for creation or edition
        """
        if not self.object:
            return _("New content")
        return _("Edit %(name)s" % {'name' : self.object.text_headline })


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


def edit_content(request, content_id = None, content_type = None):
    """
    Edit the given content or create a new one if necessary
    """
    # Get basic information
    account = request.user.get_profile()
    if content_id is not None:
        content = Content.objects.get(id = content_id)
        if not content.can_view:
            raise NotImplementedError("Should implement a permission denied exception here")
        if not content.can_edit:
            raise NotImplementedError("Should redirect to the regular view? or raise a permission denied exception here.")
        form_entry = form_registry.getFormEntries(content.model_name, edition = True)[0]
    else:
        # XXX TODO: Check some kind of "can_create_content" permission?
        content = None
        form_entry = form_registry.getFormEntries(content_type, creation = True)[0]

    # Process form
    if request.method == 'POST': # If the form has been submitted...
        if content:
            form = form_entry['form_class'](request.POST, instance = content.object)
        else:
            form = form_entry['form_class'](request.POST)
        
        if form.is_valid(): # All validation rules pass
            content = form.save()
            return HttpResponseRedirect(reverse('twistranet.views.content_by_id', args = (content.id,)))
    else:
        if content:
            form = form_entry['form_class'](instance = content.object)
        else:
            form = form_entry['form_class']()

    # Template hapiness
    t = loader.get_template('content/edit.html')
    c = RequestContext(
        request,
        {
            "account": account,
            "content": content,
            "content_type": form_entry['content_type'],
            "form": form,
        },
        )
    return HttpResponse(t.render(c))


@require_access
def create_content(request, content_type):
    """
    """
    return edit_content(request, content_type = content_type)

@require_access
def delete_content(request, content_id):
    """
    Explicit
    """
    account = request.user.get_profile()
    content = Content.objects.distinct().get(id = content_id)
    name = content.model_name
    content.delete()
    messages.info(request, _('The %(name)s has been deleted.' % {'name': name}))
    return HttpResponseRedirect(reverse('twistranet.views.home', ))


