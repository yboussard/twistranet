# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q

from twistranet.models import Content, StatusUpdate, Community, Account

from twistranet.models import ContentRegistry, Community

class MustRedirect(Exception):
    """
    Raise this if something must redirect to the current page
    """
    pass

def _getInlineForms(request, publisher = None):
    """
    - a forms list ; empty list if no form to display ;

    Return the inline forms object used to display the marvellous edition form(s).
    Process 'em, by the way.
    'publisher' is the account we're going to publish on. If none, assume it's the current user.
    """
    # Account information used to build the wall view
    account = request.user.get_profile()
    if not publisher:
        publisher = account
            
    # Wall edition forms if user has the right to write on it
    # This return a list of forms as each content type can define its own tab+form
    form_classes = ContentRegistry.getContentFormClasses(publisher)
    forms = []
    for form_class in form_classes:
        # Initial data processing
        initial = {
            "publisher_id": publisher.id,
            }
        
        # Form display / validation stuff
        if request.method != 'POST':                        # If the form has not been submitted...
            form = form_class(initial = initial)
            forms.append(form)
        else:                                               # Ok, we submited
            form = form_class(request.POST, initial = initial)
            content_type = form.getName()
            
            # We skip validation for forms of other content types.
            if request.POST.get('validated_form', None) <> content_type:
                forms.append(form_class(initial = initial))
                continue

            # Validate stuff
            if form.is_valid():                             # All validation rules pass
                # Process the data in form.cleaned_data
                c = form.save(commit = False)
                c.publisher = Account.objects.get(id = request.POST.get('publisher_id'))    # Will raise if unauthorized
                c.save()
                form.save_m2m()
                # forms.append(form_class(initial = initial)) => Silly stuff anyway?
                raise MustRedirect()
            else:
                forms.append(form)
    
    # Return the forms
    return forms



def account_by_id(request, account_id):
    """
    Account (user/profile) page.
    We just diplay posts of any given account.
    XXX TODO:
        - Check if account is listed and permit only if approved
    """
    # Get the OBJECT himself
    account = Account.objects.get(id = account_id).object
    current_account = request.user.get_profile()
    
    # If we're on a community, we should redirect
    if isinstance(account, Community):
        return HttpResponseRedirect(reverse('twistranet.views.community_by_id', args = (account.id,)))

    # Generate forms
    try:
        forms = _getInlineForms(request, publisher = account)
    except MustRedirect:
        return HttpResponseRedirect(request.path)
    
    latest_list = Content.objects.getActivityFeed(account).order_by("-date")
    t = loader.get_template('account.html')
    c = RequestContext(
        request,
        {
            'path': request.path,
            "content_forms": forms,
            "current_account": current_account,
            "account": account,
            "latest_content_list": latest_list[:25],
            
            "account_in_my_network": not not current_account.network.filter(id = account.id),
        },
        )
    return HttpResponse(t.render(c))
    

@login_required     # XXX TODO: Use the correct decorator to avoid the login_required obligation
def home(request):
    """
    The HOME page. This is the activity feed of the currently logged user.
    """
    # Account information used to build the wall view
    account = request.user.get_profile()
    try:
        forms = _getInlineForms(request)
    except MustRedirect:
        return HttpResponseRedirect(request.path)
    
    # Render the template
    latest_list = account.content.followed.order_by("-date")
    communities_list = Community.objects.get_query_set()
    t = loader.get_template('wall.html')
    c = RequestContext(
        request,
        {
            'path': request.path,
            'account': account,
            'current_account': request.user.get_profile(),
            'latest_content_list': latest_list[:25],
            'content_forms': forms,
        },
        )
    return HttpResponse(t.render(c))


