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

@require_access
def edit_content(request, content_id = None, content_type = None):
    """
    Edit the given content or create a new one if necessary
    """
    # Get basic information
    account = request.user.get_profile()
    if content_id is not None:
        content = Content.objects.distinct().get(id = content_id)
        if not content.can_view:
            raise NotImplementedError("Should implement a permission denied exception here")
        if not content.can_edit:
            raise NotImplementedError("Should redirect to the regular view? or raise a permission denied exception here.")
        form_entry = form_registry.getFormEntries(content.model_name)[0]
    else:
        # XXX TODO: Check some kind of "can_create_content" permission?
        content = None
        form_entry = form_registry.getFormEntries(content_type)[0]

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
def content_by_id(request, content_id):
    """
    Display a content
    """
    # Basic data
    account = request.user.get_profile()
    content = Content.objects.distinct().get(id = content_id)
    if not content.can_view:
        raise NotImplementedError("Should raise permission denied here.")

    # Dereference the actual underlying content object
    content = content.object
    
    # Display the view template (given by the detail_view pty of the content)
    t = loader.get_template(content.detail_view)
    c = RequestContext(
        request,
        {
            "content": content,
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


