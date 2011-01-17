import time
import mimetypes
import os
import posixpath
import re
import stat
import urllib

from django.template import Context, RequestContext, loader
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseNotModified
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import http_date

from twistranet.twistranet.models import *
from twistranet.twistranet.forms.resource_forms import ResourceForm, ResourceBrowserForm
from twistranet.twistranet.lib.decorators import require_access

from django.conf import settings
from django.views.static import was_modified_since
from twistranet.twistorage.storage import Twistorage
from twistranet.twistranet.lib import utils


def serve(request, path, document_root = None, show_indexes = False, nocache = False):
    """
    Adapted from django.views.static to handle the creation/modification date of the resource's publisher
    instead of only the file's value.
    
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root' : '/path/to/my/files/'})

    in your URLconf. You must provide the ``document_root`` param. You may
    also set ``show_indexes`` to ``True`` if you'd like to serve a basic index
    of the directory.  This index view will use the template hardcoded below,
    but if you'd like to override it, you can create a template called
    ``static/directory_index.html``.
    """

    # Clean up given path to only allow serving files below document_root.
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')
    if newpath and path != newpath:
        return HttpResponseRedirect(newpath)
    fullpath = os.path.join(document_root, newpath)
    if os.path.isdir(fullpath):
        # if show_indexes:
        #     return directory_index(newpath, fullpath)
        raise Http404("Directory indexes are not allowed here.")
    if not os.path.exists(fullpath):
        raise Http404('"%s" does not exist' % fullpath)
    
    # Respect the If-Modified-Since header.
    statobj = os.stat(fullpath)
    mimetype = mimetypes.guess_type(fullpath)[0] or 'application/octet-stream'
    # XXX TODO: Handle this correctly!!! Disabled to avoid using file mod. time instead of obj mod. time
    if not nocache:
        if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
                                  statobj[stat.ST_MTIME], statobj[stat.ST_SIZE]):
            return HttpResponseNotModified(mimetype=mimetype)
    contents = open(fullpath, 'rb').read()
    response = HttpResponse(contents, mimetype=mimetype)
    response["Last-Modified"] = http_date(statobj[stat.ST_MTIME])
    response["Content-Length"] = len(contents)
    return response



def _getResourceResponse(request, resource, last_modified = None):
    """
    Return the proper HTTP stream for a resource object
    XXX TODO: Handle the last_modified parameter
    """
    # Determinate the appropriate rendering scheme: file or URL
    if resource.resource_url:
        raise NotImplementedError("We yet have to implement resource URLs")
    
    # Resource file: get storage and check if path exists
    elif resource.resource_file:
        path = resource.resource_file.name      # XXX TODO: Handle subdirectories somehow here
        storage = Twistorage()
        if not storage.exists(path):
            raise Http404

    # Neither a file nor a URL? Then it's probably invalid.
    # Maybe we should implement an "alias" type of resource?
    else:
        raise ValueError("Invalid resource: %s" % resource)

    # Return the underlying file, adapt the Last-Modified header as necessary
    return serve(request, path, document_root = storage.location, show_indexes = False, nocache = True)
    
@require_access
def resource_cache(request, cache_path):
    """
    Return a resource by its cache path.
    XXX TODO: HANDLE SECURITY ON THIS
    """
    return serve(request, cache_path, os.path.join(settings.MEDIA_ROOT, "cache"))

@require_access
def resource_by_id(request, resource_id):
    """
    Return a resource by id
    """
    resource = Resource.objects.get(id = resource_id)
    return _getResourceResponse(request, resource)

@require_access
def resource_by_slug(request, slug):
    """
    XXX TODO: Make this more efficient?
    """
    resource = Resource.objects.get(slug = slug)
    return _getResourceResponse(request, resource)

@require_access
def resource_by_slug_or_id(request, slug_or_id):
    """
    Return a resource by its alias or by its id if not found
    """
    try:
        resource = Resource.objects.get(slug = slug_or_id)
    except ObjectDoesNotExist:
        resource = Resource.objects.get(id = slug_or_id)
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
            return HttpResponseRedirect(reverse('twistranet.twistranet.views.resource_by_id', args = (resource.id,)))
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


@require_access
def resource_browser(request):
    """
    A view used to browse and upload resources
    Based on resource field
    """
    
    form = ResourceBrowserForm()
    params = {}
    params["account"] = request.user.get_profile()
    params["actions"] = ''
    params["site_name"] = utils.get_site_name()
    params["baseline"] = utils.get_baseline()
    params['form'] = form
    template = 'resource/resource_browser_form.html'
    t = loader.get_template(template)
    c = RequestContext(
        request,
        params
        )
    return HttpResponse(t.render(c))
