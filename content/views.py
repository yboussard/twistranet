# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from TwistraNet.content.models import Content, StatusUpdate
from TwistraNet.account.models import Account

from TwistraNet.content.forms import getContentFormClass


@login_required
def account(request, account_id):
    """
    Account (user/profile) page.
    We just diplay posts of any given account.
    XXX TODO:
        - Check if account is listed and permit only if approved
    """
    account = Account.objects.get(id = account_id)
    latest_list = Content.secured(account).filter(account = account)
    t = loader.get_template('account.html')
    t = RequestContext(
        request,
        {
            "latest_content_list": latest_list,
        },
        )
    return HttpResponse(t.render(c))
    
    

@login_required
def wall(request):
    """
    The WALL page. This is the "homepage" of the currently logged user.
    """
    # Account information used to build the wall view
    account = request.user.get_profile()
    
    # Wall edition form if user has the right to write on it
    form_class = getContentFormClass(account, account)
    if request.method == 'POST':                        # If the form has been submitted...
        # Should use some method to determine the form to render here
        form = form_class(request.POST)           # A form bound to the POST data
        if form.is_valid():                             # All validation rules pass
            # Process the data in form.cleaned_data
            c = form.save(commit = False)
            c.preSave(account)
            c.save()
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = form_class() # An unbound form

    # Content displayed on the wall
    latest_list = Content.secured(account).all().order_by('-date')[:5]
    
    # Render the template
    t = loader.get_template('wall.html')
    c = RequestContext(
        request,
        {
            'latest_content_list': latest_list,
            'form': form,
        },
        )
    return HttpResponse(t.render(c))
    # Or can do:
    # return render_to_response('wall.html', {'latest_content_list': latest_content_list})
    


