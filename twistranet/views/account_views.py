# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist


from twistranet.models import Content, StatusUpdate
from twistranet.models import Account

from twistranet.models import ContentRegistry


def _getInlineForms(request, publisher = None):
    """
    Return the inline forms object used to display the marvellous edition form(s).
    Process 'em, by the way.
    'publisher' is the account we're going to publish on. If none, assume it's the current user.
    
    XXX TODO: Manage that publisher stuff
    """
    # Account information used to build the wall view
    account = request.user.get_profile()
    if not publisher:
        publisher = account
            
    # Wall edition forms if user has the right to write on it
    # This return a list of forms as each content type can define its own tab+form
    form_classes = ContentRegistry.getContentFormClasses(account, account)
    forms = []
    for form_class in form_classes:
        if request.method == 'POST':                        # If the form has been submitted...
            form = form_class(request.POST)                 # A form bound to the POST data
            content_type = form.getName()
            
            # We skip validation for forms of other content types,
            # BUT we ensure that data is bound anyway
            if not request.POST.get('validated_form', None) == content_type:
                forms.append(form_class())
                continue

            # Validate stuff
            if form.is_valid():                             # All validation rules pass
                # Process the data in form.cleaned_data
                c = form.save()
                forms.append(form_class())
                # c.save()
                # return HttpResponseRedirect('/') # Redirect after POST
            else:
                forms.append(form)
        else:
            form = form_class()
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
    account = Account.objects.get(id = account_id)
    latest_list = Content.objects.getFollowed(account = account)
    t = loader.get_template('account.html')
    c = RequestContext(
        request,
        {
            "account": account,
            "latest_content_list": latest_list[:25],
        },
        )
    return HttpResponse(t.render(c))
    


# @login_required
# def account_wall(request, account_id):
#     """
#     Display an account wall page for given user.
#     """
#     # Get current user and targeted account information
#     account = request.user.get_profile()
#     wall = account.accounts.filter(id = account_id)
#   
#     # Render the template
#     t = loader.get_template('wall.html')
#     c = RequestContext(
#         request,
#         {
#             'account': account,
#             'latest_content_list': account.content.getFollowed()[:5],
#             'forms': forms,
#         },
#         )
#     return HttpResponse(t.render(c))
#  

@login_required
def home(request):
    """
    The HOME page. This is the activity feed of the currently logged user.
    """
    # Account information used to build the wall view
    account = request.user.get_profile()
    forms = _getInlineForms(request)
    
    # Render the template
    t = loader.get_template('wall.html')
    c = RequestContext(
        request,
        {
            'account': account,
            'latest_content_list': account.content.getFollowed()[:25],
            'forms': forms,
        },
        )
    return HttpResponse(t.render(c))
    # Or can do:
    # return render_to_response('wall.html', {'latest_content_list': latest_content_list})
    


