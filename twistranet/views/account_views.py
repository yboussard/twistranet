# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from twistranet.models import *
from twistranet.lib import form_registry
from twistranet.lib.decorators import require_access

# XXX Move this is settings
TWISTRANET_CONTENT_PER_PAGE = 25

# XXX For some obscure reason, I've got a dirty django error when trying to select_related content_types.
# I have to find how and why... but perhaps subtypes are not needed in account page, thanks to the xxx_summary/xxx_headline fields?
select_related_summary_fields = (
    # "notification",
    # "statusupdate",
    "author",
    "publisher",
)

class MustRedirect(Exception):
    """
    Raise this if something must redirect to the current page
    """
    pass

@require_access
def _getInlineForms(request, publisher = None):
    """
    - a forms list ; empty list if no form to display ;

    Return the inline forms object used to display the marvellous edition form(s).
    Process 'em, by the way.
    'publisher' is the account we're going to publish on. If none, assume it's the current user.
    """
    # Account information used to build the wall view
    account = Account.objects._getAuthenticatedAccount()
    if not account or account.is_anonymous:
        return []       # Anonymous can't do that much things...
    if not publisher:
        publisher = account
            
    # Wall edition forms if user has the right to write on it
    # This return a list of forms as each content type can define its own tab+form
    form_classes = form_registry.getInlineForms(publisher)
    forms = []
    for form_class in [ k['form_class'] for k in form_classes ]:
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

@require_access
def account_by_alias_or_id(request, alias):
    """
    XXX TODO
    """
    raise NotImplementedError

@require_access
def account_by_id(request, account_id):
    """
    Account (user/profile) page.
    We just diplay posts of any given account.
    XXX TODO:
        - Check if account is listed and permit only if approved
    """
    # Get the OBJECT himself
    # XXX Same as select_related_summary_fields: I've got a "'account' is not an ancestor of this model" error from django
    # when trying to select related useraccount field. Grrr.
    # By adding "return None" in django/db/models/options.py:433 (in get_base_chain), it seems to work.
    # account = Account.objects.select_related('useraccount').get(id = account_id).object
    account = Account.objects.get(id = account_id).object
    
    # If we're on a community, we should redirect
    if isinstance(account, Community):
        return HttpResponseRedirect(reverse('twistranet.views.community_by_id', args = (account.id,)))

    # Generate forms
    try:
        forms = _getInlineForms(request, publisher = account)
    except MustRedirect:
        return HttpResponseRedirect(request.path)
        
    # Generate the latest content list. We first get the first X ids, then re-issue the query with a generous select_related.
    # This way, we just issue a couple of queries instead of a bunch of requests!
    # This replaces the following line:
    # latest_list = Content.objects.getActivityFeed(account).order_by("-created_at").distinct()[:TWISTRANET_CONTENT_PER_PAGE]
    latest_ids = Content.objects.getActivityFeed(account).values_list('id', flat = True).order_by("-created_at").distinct()[:TWISTRANET_CONTENT_PER_PAGE]
    latest_list = Content.objects.__booster__.filter(id__in = tuple(latest_ids)).select_related(*select_related_summary_fields).order_by("-created_at")

    # Generate the view itself
    current_account = Account.objects._getAuthenticatedAccount()
    t = loader.get_template('account/view.html')
    c = RequestContext(
        request,
        {
            'path': request.path,
            "content_forms": forms,
            "account": account,
            "latest_content_list": latest_list,
            "account_in_my_network": not current_account.is_anonymous and not not current_account.network.filter(id = account.id),
        },
        )
    return HttpResponse(t.render(c))
    
@require_access
def account_by_slug(request, slug):
    """
    XXX TODO: Make this more efficient?
    """
    account = Account.objects.get(slug = slug)
    return account_by_id(request, account.id)

@require_access
def home(request):
    """
    The HOME page. This is the activity feed of the currently logged user.
    """
    # Account information used to build the wall view
    try:
        forms = _getInlineForms(request)
    except MustRedirect:
        return HttpResponseRedirect(request.path)
    
    account = Account.objects._getAuthenticatedAccount()
    if account and not isinstance(account, AnonymousAccount):
        # Generate the latest content list. We first get the first X ids, then re-issue the query with a generous select_related.
        # This way, we just issue a couple of queries instead of a bunch of requests!
        # We also do the discinct part by hand, assuming each content can be duplicated at most 10 times XXX Calculate that more precisely!
        # This replaces the following line:
        # latest_list = Content.objects.getActivityFeed(account).order_by("-created_at").distinct()[:TWISTRANET_CONTENT_PER_PAGE]
        latest_ids = account.content.followed.values_list('id', flat = True).order_by("-created_at")[:TWISTRANET_CONTENT_PER_PAGE * 10]
        latest = {}
        [ latest.__setitem__(i, None) for i in latest_ids ]
        latest_list = Content.objects.__booster__.filter(id__in = latest.keys()).select_related(*select_related_summary_fields).order_by("-created_at")
    else:
        # Just return public content
        latest_list = Content.objects.order_by("-created_at")
        
    # Render the template
    communities_list = Community.objects.get_query_set()
    t = loader.get_template('wall.html')
    c = RequestContext(
        request,
        {
            "account": not account.is_anonymous and account,
            'path': request.path,
            'latest_content_list': latest_list[:TWISTRANET_CONTENT_PER_PAGE],
            'content_forms': forms,
        },
        )
    return HttpResponse(t.render(c))


