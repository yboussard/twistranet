from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from twistranet.models import *
from twistranet.forms.resource_forms import ResourceForm
from twistranet.lib.decorators import require_access

def _getResourceResponse(request, resource):
    """
    Return the proper HTTP stream for a resource object
    """
    return HttpResponse(
        resource.get(),
        content_type = resource.mimetype,
        )

@require_access
def resource_by_id(request, resource_id):
    """
    Return a resource by id
    """
    resource = Resource.objects.get(id = resource_id)
    return _getResourceResponse(request, resource)

@require_access
def resource_by_alias_or_id(request, alias_or_id):
    """
    Return a resource by its alias or by its id if not found
    """
    try:
        resource = Resource.objects.get(alias = alias_or_id)
    except ObjectDoesNotExist:
        resource = by_id(request, alias_or_id)
    return _getResourceResponse(request, resource)
    
@require_access
def resource_by_account(request, account_id, property):
    """
    Fetch a resource by an account attribute.
    """
    account = Account.objects.get(id = account_id)
    resource = getattr(account, property, None)
    if isinstance(resource, Resource):
        return _getResourceResponse(request, resource)
    else:
        # XXX should raise 404 if pty not found
        raise ValueError("Invalid property")
        
@require_access
def resource_by_content(request, content_id, property):
    """
    Fetch a resource by an content attribute.
    """
    content = Content.objects.get(id = content_id)
    resource = getattr(content, property, None)
    if isinstance(resource, Resource):
        return _getResourceResponse(request, resource)
    else:
        # XXX should raise 404 if pty not found
        raise ValueError("Invalid property")

@require_access
def edit_resource(request, resource_id = None):
    """
    Edit the given resource or create a new one if necessary
    """
    # Get basic information
    account = request.user.get_profile()
    if resource_id is not None:
        resource = Resource.objects.get(id = resource_id)
        # XXX TODO: Implement security here.
        # if not resource.can_view:
        #     raise NotImplementedError("Should implement a permission denied exception here")
        # if not resource.can_edit:
        #     raise NotImplementedError("Should redirect to the regular view? or raise a permission denied exception here.")
        # form_entry = form_registry.getFormEntry(content.content_type)
    else:
        # XXX TODO: Check some kind of "can_create_content" permission?
        resource = None
        # form_entry = form_registry.getFormEntry(content_type)

    # Process form
    if request.method == 'POST': # If the form has been submitted...
        if resource:
            form = ResourceForm(request.POST, request.FILES, instance = resource)
        else:
            form = ResourceForm(request.POST, request.FILES)

        if form.is_valid():
            return HttpResponseRedirect(reverse('twistranet.views.resource_by_id', args = (resource.id,)))
    else:
        if resource:
            form = ResourceForm(instance = resource.object)
        else:
            form = ResourceForm()

    # Template hapiness
    t = loader.get_template('resource/edit.html')
    c = RequestContext(
        request,
        {
            "account": account,
            "resource": resource,
            "form": form,
        },
        )
    return HttpResponse(t.render(c))

@require_access
def create_resource(request):
    """
    """
    return edit_resource(request)


        