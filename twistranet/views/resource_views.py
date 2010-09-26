# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from twistranet.models import *


def _getResourceResponse(request, resource):
    """
    Return the proper HTTP stream for a resource object
    """
    return HttpResponse(
        resource.get(),
        content_type = resource.mimetype,
        )

def resource_by_id(request, resource_id):
    """
    Return a resource by id
    """
    resource = Resource.objects.get(id = resource_id)
    return _getResourceResponse(request, resource)

def resource_by_alias_or_id(request, alias_or_id):
    """
    Return a resource by its alias or by its id if not found
    """
    try:
        resource = Resource.objects.get(alias = alias_or_id)
    except ObjectDoesNotExist:
        resource = by_id(request, alias_or_id)
    return _getResourceResponse(request, resource)
    
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




        