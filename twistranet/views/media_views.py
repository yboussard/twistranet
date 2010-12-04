from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse


from twistranet.models import *
from twistranet.forms.resource_forms import MediaForm
from twistranet.lib.decorators import require_access

@require_access
def edit_media(request, resource_id = None):
    """
    Edit the given media resource or create a new one if necessary
    XXX Todo: Check if the resource is a real media!
    """
    # Get basic information
    account = request.user.get_profile()
    if resource_id is not None:
        raise NotImplementedError
        # media = media.objects.get(id = media_id)
        # XXX TODO: Implement security here.
        # if not media.can_view:
        #     raise NotImplementedError("Should implement a permission denied exception here")
        # if not media.can_edit:
        #     raise NotImplementedError("Should redirect to the regular view? or raise a permission denied exception here.")
        # form_entry = form_registry.getFormEntry(content.content_type)
    else:
        # XXX TODO: Check some kind of "can_create_content" permission?
        media = None
        # form_entry = form_registry.getFormEntry(content_type)


    # Process form
    if request.method == 'POST': # If the form has been submitted...
        if media:
            raise NotImplementedError
            # form = MediaForm(request.POST, instance = media)
        else:
            form = MediaForm(request.POST, request.FILES, )

        if form.is_valid(): # All validation rules pass
            print "validation rules applied"
            media = account.media_resource_manager.uploadResource(request.FILES['file'])
            return HttpResponseRedirect(reverse('twistranet.views.view_media_library', args = (account.id,)))
    else:
        if media:
            raise NotImplementedError
            form = MediaForm(instance = media.object)
        else:
            form = MediaForm()

    # Template hapiness
    t = loader.get_template('resource/edit.html')
    c = RequestContext(
        request,
        {
            "account": account,
            "media": media,
            "form": form,
        },
        )
    return HttpResponse(t.render(c))

@require_access
def create_media(request):
    """
    """
    return edit_media(request)

@require_access
def view_media_library(request, account_id):
    """
    View a media library for the given account.
    Only return permitted resources (of course).
    """
    # Get the OBJECT himself
    account = Account.objects.select_related('useraccount').get(id = account_id).object
    current_account = request.user.get_profile()
    latest_list = Resource.objects.filter(owner = account).order_by("-created_at")

    # Generate the view itself
    t = loader.get_template('resource/view_media_library.html')
    c = RequestContext(
        request,
        {
            "account": account,
            "media_list": latest_list,
        },
        )
    return HttpResponse(t.render(c))


