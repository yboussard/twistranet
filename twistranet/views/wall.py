# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from twistranet.models import Content, StatusUpdate
from twistranet.models import Account

from twistranet.models import ContentRegistry


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
    
    # Wall edition forms if user has the right to write on it
    # This return a list of forms as each content type can define its own tab+form
    form_classes = ContentRegistry.getContentFormClasses(account, account)
    forms = []
    for form_class in form_classes:
        content_type = form_class.Meta.model.__name__
        if request.method == 'POST':                        # If the form has been submitted...
            form = form_class(request.POST)           # A form bound to the POST data
            
            # We skip validation for forms of other content types,
            # BUT we ensure that data is bound anyway
            if not form.data['content_type'] == content_type:
                forms.append(form_class(request.POST))
                continue

            # Validate stuff
            if form.is_valid():                             # All validation rules pass
                # Process the data in form.cleaned_data
                c = account.content.bound(form.save(commit = False))
                c.save()
                return HttpResponseRedirect('/') # Redirect after POST
        else:
            form = form_class({
                # Keep track of the content_type to ensure proper validation
                'content_type': content_type,
                })
        forms.append(form)

    # Render the template
    t = loader.get_template('wall.html')
    c = RequestContext(
        request,
        {
            'account': account,
            'latest_content_list': account.content.followed[:5],
            'forms': forms,
        },
        )
    return HttpResponse(t.render(c))
    # Or can do:
    # return render_to_response('wall.html', {'latest_content_list': latest_content_list})
    


